from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
from werkzeug.security import generate_password_hash, check_password_hash
import secrets
import string
import datetime
import uuid
from sqlalchemy import text
from flask_migrate import Migrate



app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECRET_KEY'] = 'd493d1e49bda245f76d2ee9855cffacf'

app.config['MAIL_SERVER'] = 'mail.euroalfa.eu'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USERNAME'] = 'stb@euroalfa.eu'
app.config['MAIL_PASSWORD'] = 'Q[pfP@n8R+v['
app.config['MAIL_TIMEOUT'] = 10

db = SQLAlchemy(app)
mail = Mail(app)
migrate = Migrate(app, db)

# Database Models

class User(db.Model):
    userId = db.Column(db.String(50), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    travel_card_id = db.Column(db.String(50), db.ForeignKey('travel_card.cardId'))


class TravelCard(db.Model):
    cardId = db.Column(db.String(50), primary_key=True)
    balance = db.Column(db.Float, default=0.0)

class Ticket(db.Model):
    ticketId = db.Column(db.String(50), primary_key=True)
    user_id = db.Column(db.String(50), db.ForeignKey('user.userId'))
    type = db.Column(db.String(20), nullable=False)
    price = db.Column(db.Float, nullable=False)
    valid = db.Column(db.Boolean, default=True)
    purchase_time = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    expiry = db.Column(db.DateTime, nullable=True)

class Payment(db.Model):
    paymentId = db.Column(db.String(50), primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    date = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    user_id = db.Column(db.String(50), db.ForeignKey('user.userId'))

class Journey(db.Model):
    journeyId = db.Column(db.String(50), primary_key=True)
    origin = db.Column(db.String(100), nullable=False)
    destination = db.Column(db.String(100), nullable=False)
    estimatedTime = db.Column(db.String(50))
    user_id = db.Column(db.String(50), db.ForeignKey('user.userId'))
    active = db.Column(db.Boolean, default=True)
    route_id = db.Column(db.String(50))

# Routes for Public Users

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        raw_password = request.form['password']

        # Check if email already exists
        if User.query.filter_by(email=email).first():
            flash('Email already registered. Please use a different email.', 'error')
            return render_template('register.html', name=name, email=email)

        hashed_password = generate_password_hash(raw_password, method='pbkdf2:sha256')
        user_id = str(uuid.uuid4())
        new_user = User(userId=user_id, name=name, email=email, password=hashed_password)
        new_card = TravelCard(cardId=user_id, balance=0.0)
        db.session.add(new_card)
        new_user.travel_card_id = user_id
        db.session.add(new_user)
        db.session.commit()

        try:
            msg = Message(
                subject="Welcome to STB!",
                sender=app.config['MAIL_USERNAME'],
                recipients=[email]
            )
            msg.body = f"Welcome {name} to STB!\n\nThis is your card number: {user_id}\n\nAll the best,\nSTB Team"
            mail.send(msg)
        except Exception as e:
            flash(f"Registration successful, but email could not be sent: {e}", "error")
            return redirect(url_for('login'))
        
        flash('Registration successful. Please login.')
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        raw_password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, raw_password):
            session['user_id'] = user.userId
            session['is_admin'] = user.is_admin
            flash('Logged in successfully.')
            if user.is_admin:
                return redirect(url_for('admin_dashboard'))
            else:
                return redirect(url_for('dashboard'))
        else:
            flash('Incorrect email or password.')
            return redirect(url_for('login'))
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('is_admin', None)
    flash('Logged out successfully.')
    return redirect(url_for('login'))


@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user = User.query.filter_by(userId=session['user_id']).first()
    if not user:
        flash('User not found. Please log in again.')
        session.pop('user_id', None)
        session.pop('is_admin', None)
        return redirect(url_for('login'))
    travel_card = TravelCard.query.get(user.travel_card_id)
    tickets = Ticket.query.filter_by(user_id=user.userId).all()

    with db.engine.connect() as conn:
        journeys = Journey.query.filter_by(user_id=user.userId).all()
        journey_details = []
        for journey in journeys:
            stations = conn.execute(
                text("SELECT station_name, arrival_time, departure_time FROM route_stations WHERE route_id = :route_id ORDER BY station_order"),
                {"route_id": journey.route_id}
            ).fetchall()
            departure_time = stations[0].departure_time if stations else None
            journey_details.append({
                "journey": journey,
                "stations": stations,
                "departure_time": departure_time
            })

    return render_template(
        'dashboard.html',
        user=user,
        travel_card=travel_card,
        tickets=tickets,
        journey_details=journey_details
    )

@app.route('/reset_password', methods=['GET', 'POST'])
def reset_password():
    if request.method == 'POST':
        email = request.form['email']
        user = User.query.filter_by(email=email).first()
        if user:
            # Generate a new random password
            new_password = ''.join(secrets.choice(string.ascii_letters + string.digits) for i in range(8))
            user.password = generate_password_hash(new_password, method='pbkdf2:sha256')
            db.session.commit()
            msg = Message("Password Reset", sender=app.config['MAIL_USERNAME'], recipients=[email])
            msg.body = f"Your new password is: {new_password}"
            mail.send(msg)
            flash('A new password has been sent to your email.')
            return redirect(url_for('login'))
        else:
            flash('Email not found.')
            return redirect(url_for('reset_password'))
    return render_template('reset_password.html')

def generate_times(start, end, interval):
    from datetime import datetime, timedelta
    times = []
    today = datetime.today()
    t = datetime.strptime(start, "%H:%M")
    end_t = datetime.strptime(end, "%H:%M")
    while t <= end_t:
        times.append(t.strftime("%H:%M"))
        t += timedelta(minutes=interval)
    return times



@app.route('/schedule_journey', methods=['GET', 'POST'])
def schedule_journey():
    if 'user_id' not in session or session.get('is_admin'):
        return redirect(url_for('login'))
    with db.engine.connect() as conn:
        train_routes = conn.execute(
            text("SELECT * FROM routes WHERE transport_type = 'train'")
        ).fetchall()
        selected_route_id = request.form.get('route_id') if request.method == 'POST' else None
        stations = []
        if selected_route_id:
            stations = conn.execute(
                text("SELECT station_name FROM route_stations WHERE route_id = :route_id ORDER BY station_order"),
                {"route_id": selected_route_id}
            ).fetchall()
    if request.method == 'POST':
        route_id = request.form.get('route_id')
        origin = request.form.get('origin')
        destination = request.form.get('destination')
        # Only save if both origin and destination are provided
        if route_id and origin and destination:
            journey = Journey(
                journeyId=secrets.token_hex(4),
                user_id=session['user_id'],
                origin=origin,
                destination=destination,
                route_id=route_id
            )
            db.session.add(journey)
            db.session.commit()
            flash('Train journey scheduled successfully!')
            return redirect(url_for('dashboard'))
        else:
            flash('Please select both origin and destination.', 'error')
    return render_template('schedule_journey.html', train_routes=train_routes, stations=stations)


@app.route('/buy_ticket', methods=['GET', 'POST'])
def buy_ticket():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user = User.query.filter_by(userId=session['user_id']).first()
    travel_card = TravelCard.query.get(user.travel_card_id)
    if request.method == 'POST':
        ticket_type = request.form['ticket_type']
        price = float(request.form['price'])
        # Check if balance is sufficient
        if travel_card.balance < price:
            flash('Insufficient balance to purchase this ticket.', 'error')
            return render_template('buy_ticket.html', travel_card=travel_card)
        
        now = datetime.datetime.utcnow()
        if ticket_type == 'daily':
            expiry = now + datetime.timedelta(days=1)
        elif ticket_type == 'monthly':
            expiry = now + datetime.timedelta(days=30)
        else:
            expiry = None
        new_ticket = Ticket(
            ticketId=secrets.token_hex(4),
            user_id=session['user_id'],
            type=ticket_type,
            price=price,
            valid=True,
            purchase_time=now,
            expiry=expiry
        )
        db.session.add(new_ticket)
        travel_card.balance -= price
        db.session.commit()
        flash('Ticket purchased successfully.')
        return redirect(url_for('dashboard'))
    return render_template('buy_ticket.html', travel_card=travel_card)


@app.route('/topup', methods=['GET', 'POST'])
def topup():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        amount = float(request.form['amount'])
        user = User.query.filter_by(userId=session['user_id']).first()
        travel_card = TravelCard.query.get(user.travel_card_id)
        travel_card.balance += amount
        # Record payment transaction.
        payment = Payment(
            paymentId=secrets.token_hex(4),
            amount=amount,
            user_id=user.userId
        )
        db.session.add(payment)
        db.session.commit()
        flash('Travel card topped up successfully.')
        return redirect(url_for('dashboard'))
    return render_template('topup.html')


@app.route('/route_search', methods=['GET', 'POST'])
def route_search():
    with db.engine.connect() as conn:
        routes = conn.execute(text("SELECT * FROM routes")).fetchall()
        stations = conn.execute(text("SELECT DISTINCT station_name FROM route_stations")).fetchall()
        transport_types = conn.execute(text("SELECT DISTINCT transport_type FROM routes")).fetchall()
        route_ids = conn.execute(text("SELECT DISTINCT route_id FROM routes")).fetchall()

        selected_mode = request.args.get('mode')
        selected_station = request.args.get('station')
        selected_time = request.args.get('time')

        query = "SELECT r.*, rs.station_name, rs.arrival_time, rs.departure_time FROM routes r JOIN route_stations rs ON r.route_id = rs.route_id WHERE 1=1"
        params = {}
        if selected_mode:
            query += " AND r.transport_type = :mode"
            params['mode'] = selected_mode
        if selected_station:
            query += " AND rs.station_name = :station"
            params['station'] = selected_station
        if selected_time:
            query += " AND (rs.arrival_time = :time OR rs.departure_time = :time)"
            params['time'] = selected_time

        filtered_routes = conn.execute(text(query), params).fetchall()
        

    return render_template(
        'route_search.html',
        routes=filtered_routes,
        all_lines=[row[0] for row in route_ids],  
        all_modes=[row[0] for row in transport_types],
        all_stations=[row[0] for row in stations],
        selected_mode=selected_mode,
        selected_station=selected_station,
        selected_time=selected_time
    )


@app.route('/end_journey/<journey_id>')
def end_journey(journey_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    journey = Journey.query.filter_by(journeyId=journey_id, user_id=session['user_id']).first()
    if journey:
        journey.active = False
        db.session.commit()
        flash('Journey ended successfully.')
    return redirect(url_for('dashboard'))


# Admin Routes

@app.route('/admin')
def admin_dashboard():
    if 'user_id' not in session or not session.get('is_admin'):
        flash('Admin access required.')
        return redirect(url_for('login'))
    users = User.query.all()
    travel_cards = TravelCard.query.all()
    tickets = Ticket.query.all()
    payments = Payment.query.all()
    journeys = Journey.query.all()
    return render_template('admin_dashboard.html',
                           users=users,
                           travel_cards=travel_cards,
                           tickets=tickets,
                           payments=payments,
                           journeys=journeys)


@app.route('/admin/schedule', methods=['GET', 'POST'])
def admin_schedule():
    if 'user_id' not in session or not session.get('is_admin'):
        flash('Admin access required.')
        return redirect(url_for('login'))
    schedule_data = ""
    if request.method == 'POST':
        schedule_data = request.form['schedule_data']
        flash('Schedule updated successfully.')
    return render_template('admin_schedule.html', schedule_data=schedule_data)



@app.route('/admin/users', methods=['GET', 'POST'])
def admin_users():
    if 'user_id' not in session or not session.get('is_admin'):
        return redirect(url_for('admin_login'))
    users = User.query.all()
    return render_template('admin_users.html', users=users)

@app.route('/admin/travelcards', methods=['GET', 'POST'])
def admin_travelcards():
    if 'user_id' not in session or not session.get('is_admin'):
        return redirect(url_for('admin_login'))
    search_email = request.form.get('search_email') if request.method == 'POST' else None
    if search_email:
        user = User.query.filter_by(email=search_email).first()
        travelcards = [TravelCard.query.get(user.travel_card_id)] if user else []
    else:
        travelcards = TravelCard.query.all()
    return render_template('admin_travelcards.html', travelcards=travelcards, search_email=search_email or "")

@app.route('/admin/tickets', methods=['GET', 'POST'])
def admin_tickets():
    if 'user_id' not in session or not session.get('is_admin'):
        return redirect(url_for('admin_login'))
    search_email = request.form.get('search_email') if request.method == 'POST' else None
    if search_email:
        user = User.query.filter_by(email=search_email).first()
        tickets = Ticket.query.filter_by(user_id=user.userId).all() if user else []
    else:
        tickets = Ticket.query.all()
    return render_template('admin_tickets.html', tickets=tickets, search_email=search_email or "")

@app.route('/admin/payments', methods=['GET', 'POST'])
def admin_payments():
    if 'user_id' not in session or not session.get('is_admin'):
        return redirect(url_for('admin_login'))
    search_email = request.form.get('search_email') if request.method == 'POST' else None
    if search_email:
        user = User.query.filter_by(email=search_email).first()
        payments = Payment.query.filter_by(user_id=user.userId).all() if user else []
    else:
        payments = Payment.query.all()
    return render_template('admin_payments.html', payments=payments, search_email=search_email or "")

@app.route('/admin/journeys')
def admin_journeys():
    if 'user_id' not in session or not session.get('is_admin'):
        return redirect(url_for('admin_login'))
    journeys = Journey.query.all()
    return render_template('admin_journeys.html', journeys=journeys)

@app.route('/admin/routes')
def admin_routes():
    if 'user_id' not in session or not session.get('is_admin'):
        return redirect(url_for('admin_login'))

    with db.engine.connect() as conn:
        routes = conn.execute(text("SELECT * FROM routes")).fetchall()
        stops = conn.execute(text("SELECT * FROM route_stations")).fetchall()

    return render_template('admin_routes.html', routes=routes, stops=stops)

@app.route('/admin/buy_ticket', methods=['POST'])
def admin_buy_ticket():
    if 'user_id' not in session or not session.get('is_admin'):
        return redirect(url_for('admin_login'))
    email = request.form.get('email')
    ticket_type = request.form.get('ticket_type')
    price = float(request.form.get('price'))
    user = User.query.filter_by(email=email).first()
    if not user:
        flash('User not found.', 'error')
        return redirect(url_for('admin_tickets'))
    travel_card = TravelCard.query.get(user.travel_card_id)
    if travel_card.balance < price:
        flash('Insufficient balance on user\'s travel card.', 'error')
        return redirect(url_for('admin_tickets'))

    now = datetime.datetime.utcnow()
    if ticket_type == 'daily':
        expiry = now + datetime.timedelta(days=1)
    elif ticket_type == 'monthly':
        expiry = now + datetime.timedelta(days=30)
    else:
        expiry = None

    new_ticket = Ticket(
        ticketId=secrets.token_hex(4),
        user_id=user.userId,
        type=ticket_type,
        price=price,
        valid=True,
        purchase_time=now,
        expiry=expiry
    )
    db.session.add(new_ticket)
    travel_card.balance -= price
    db.session.commit()
    flash('Ticket purchased for user successfully.')
    return redirect(url_for('admin_tickets'))

@app.route('/admin/topup', methods=['POST'])
def admin_topup():
    if 'user_id' not in session or not session.get('is_admin'):
        return redirect(url_for('admin_login'))
    email = request.form.get('email')
    amount = float(request.form.get('amount'))
    user = User.query.filter_by(email=email).first()
    if not user:
        flash('User not found.', 'error')
        return redirect(url_for('admin_travelcards'))
    travel_card = TravelCard.query.get(user.travel_card_id)
    if not travel_card:
        flash('Travel card not found for this user.', 'error')
        return redirect(url_for('admin_travelcards'))

    travel_card.balance += amount
    payment = Payment(
        paymentId=secrets.token_hex(4),
        amount=amount,
        user_id=user.userId
    )
    db.session.add(payment)
    db.session.commit()
    flash('Travel card topped up successfully for user.')
    return redirect(url_for('admin_travelcards'))

@app.route('/admin/add_route', methods=['POST'])
def admin_add_route():
    if 'user_id' not in session or not session.get('is_admin'):
        return redirect(url_for('admin_login'))
    route_id = request.form.get('route_id')
    transport_type = request.form.get('transport_type')
    start_station = request.form.get('start_station')
    end_station = request.form.get('end_station')
    with db.engine.connect() as conn:
        conn.execute(
            text("INSERT INTO routes (route_id, transport_type, start_station, end_station) VALUES (:route_id, :transport_type, :start_station, :end_station)"),
            {"route_id": route_id, "transport_type": transport_type, "start_station": start_station, "end_station": end_station}
        )
    flash('Route added successfully.')
    return redirect(url_for('admin_routes'))

@app.route('/admin/add_stop', methods=['POST'])
def admin_add_stop():
    if 'user_id' not in session or not session.get('is_admin'):
        return redirect(url_for('admin_login'))
    route_id = request.form.get('route_id')
    station_name = request.form.get('station_name')
    arrival_time = request.form.get('arrival_time')
    departure_time = request.form.get('departure_time')
    station_order = request.form.get('station_order')  # Get from form

    with db.engine.connect() as conn:
        conn.execute(
            text("INSERT INTO route_stations (route_id, station_name, arrival_time, departure_time, station_order) VALUES (:route_id, :station_name, :arrival_time, :departure_time, :station_order)"),
            {
                "route_id": route_id,
                "station_name": station_name,
                "arrival_time": arrival_time if arrival_time else None,
                "departure_time": departure_time if departure_time else None,
                "station_order": int(station_order) if station_order else 0
            }
        )
    flash('Stop added successfully.')
    return redirect(url_for('admin_routes'))

@app.route('/admin/delete_route/<route_id>', methods=['POST'])
def admin_delete_route(route_id):
    if 'user_id' not in session or not session.get('is_admin'):
        return redirect(url_for('admin_login'))
    with db.engine.connect() as conn:
        conn.execute(text("DELETE FROM route_stations WHERE route_id = :route_id"), {"route_id": route_id})
        conn.execute(text("DELETE FROM routes WHERE route_id = :route_id"), {"route_id": route_id})
    flash('Route deleted successfully.')
    return redirect(url_for('admin_routes'))


@app.route('/admin/edit_route/<route_id>', methods=['GET', 'POST'])
def admin_edit_route(route_id):
    if 'user_id' not in session or not session.get('is_admin'):
        return redirect(url_for('admin_login'))
    with db.engine.connect() as conn:
        if request.method == 'POST':
            transport_type = request.form.get('transport_type')
            start_station = request.form.get('start_station')
            end_station = request.form.get('end_station')
            conn.execute(
                text("UPDATE routes SET transport_type = :transport_type, start_station = :start_station, end_station = :end_station WHERE route_id = :route_id"),
                {
                    "route_id": route_id,
                    "transport_type": transport_type,
                    "start_station": start_station,
                    "end_station": end_station
                }
            )
            flash('Route updated successfully.')
            return redirect(url_for('admin_routes'))
        route = conn.execute(text("SELECT * FROM routes WHERE route_id = :route_id"), {"route_id": route_id}).fetchone()
        if not route:
            flash('Route not found.', 'error')
            return redirect(url_for('admin_routes'))
    return render_template('admin_edit_route.html', route=route)

@app.route('/admin/delete_stop/<route_id>/<int:station_order>', methods=['POST'])
def admin_delete_stop(route_id, station_order):
    if 'user_id' not in session or not session.get('is_admin'):
        return redirect(url_for('admin_login'))
    with db.engine.connect() as conn:
        conn.execute(
            text("DELETE FROM route_stations WHERE route_id = :route_id AND station_order = :station_order"),
            {"route_id": route_id, "station_order": station_order}
        )
    flash('Stop deleted successfully.')
    return redirect(url_for('admin_routes'))


@app.route('/admin/edit_stop/<route_id>/<int:station_order>', methods=['GET', 'POST'])
def admin_edit_stop(route_id, station_order):
    if 'user_id' not in session or not session.get('is_admin'):
        return redirect(url_for('admin_login'))
    with db.engine.connect() as conn:
        if request.method == 'POST':
            station_name = request.form.get('station_name')
            arrival_time = request.form.get('arrival_time')
            departure_time = request.form.get('departure_time')
            conn.execute(
                text("""
                    UPDATE route_stations
                    SET station_name = :station_name,
                        arrival_time = :arrival_time,
                        departure_time = :departure_time
                    WHERE route_id = :route_id AND station_order = :station_order
                """),
                {
                    "station_name": station_name,
                    "arrival_time": arrival_time if arrival_time else None,
                    "departure_time": departure_time if departure_time else None,
                    "route_id": route_id,
                    "station_order": station_order
                }
            )
            flash('Stop updated successfully.')
            return redirect(url_for('admin_routes'))
        stop = conn.execute(
            text("SELECT * FROM route_stations WHERE route_id = :route_id AND station_order = :station_order"),
            {"route_id": route_id, "station_order": station_order}
        ).fetchone()
        if not stop:
            flash('Stop not found.', 'error')
            return redirect(url_for('admin_routes'))
    return render_template('admin_edit_stop.html', stop=stop)

@app.route('/validate_ticket', methods=['GET', 'POST'])
def validate_ticket():
    if 'user_id' not in session or not session.get('is_admin'):
        flash('Admin access required.')
        return redirect(url_for('login'))
    validation_result = None
    if request.method == 'POST':
        ticket_number = request.form.get('ticket_number')
        ticket = Ticket.query.filter_by(ticketId=ticket_number).first()
        if ticket:
            user = User.query.filter_by(userId=ticket.user_id).first()
            travel_card = TravelCard.query.get(user.travel_card_id) if user else None
            if ticket.valid:
                if ticket.type == 'single':
                    db.session.delete(ticket)
                    db.session.commit()
                # For daily/monthly, do nothing (ticket remains valid until expiry)
                validation_result = {
                    "message": f"Validation successfully for {user.name} with ticket number {ticket.ticketId} and travel card {travel_card.cardId if travel_card else 'N/A'}.",
                    "success": True,
                    "user": user,
                    "ticket": ticket,
                    "travel_card": travel_card
                }
            else:
                validation_result = {"message": "Ticket already used or expired.", "success": False}
        else:
            validation_result = {"message": "Ticket not found.", "success": False}
    return render_template('admin_validate.html', validation_result=validation_result)

# Run the Application
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, host="0.0.0.0")