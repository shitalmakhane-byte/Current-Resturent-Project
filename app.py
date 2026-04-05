import os
from flask import Flask, render_template, url_for, request, redirect, flash, session
from dotenv import load_dotenv
from models import db, User, CartItem, Order, OrderItem
from functools import wraps

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')

# Fix Railway's postgres:// to postgresql:// for SQLAlchemy compatibility
_db_url = os.getenv('DATABASE_URL', 'sqlite:///restaurant.db').strip()
if _db_url.startswith('postgres://'):
    _db_url = _db_url.replace('postgres://', 'postgresql://', 1)
app.config['SQLALCHEMY_DATABASE_URI'] = _db_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db.init_app(app)

# Known menu items with fixed server-side prices (prevents price tampering)
MENU_ITEMS = {
    'Veg Biryani':              ('Veg', 120),
    'Aloo Paratha':             ('Veg', 150),
    'Dal Tadka':                ('Veg', 120),
    'Aloo Gobi':                ('Veg', 180),
    'Pani Puri':                ('Street Chaat', 50),
    'Samosa':                   ('Street Chaat', 40),
    'Missal Pav':               ('Street Chaat', 150),
    'Chole Bhature':            ('Street Chaat', 60),
    'Paneer Tikha':             ('Gym', 260),
    'Palak Paneer':             ('Gym', 280),
    'Rajma Chawal':             ('Gym', 100),
    'Avocado Toast':            ('Gym', 290),
    'Mint Cucumber Water':      ('Detox', 50),
    'Carrot Beetroot Juice':    ('Detox', 50),
    'Coconut Water Chia Seeds': ('Detox', 120),
    'Aloe Vera Juice':          ('Detox', 60),
    'Avocado Smoothie':         ('Shakes', 320),
    'Almond Milk':              ('Shakes', 70),
    'Banana Peanut Butter Shake': ('Shakes', 110),
    'Gajar Halwa':              ('Desserts', 250),
    'Cow milk Kheer':           ('Desserts', 160),
    'Dryfruit Barfi':           ('Desserts', 190),
    'Gulab Jamum':              ('Desserts', 90),
    'Vanilla Ice Cream':        ('Ice Cream', 160),
    'Dryfruit Ice Cream':       ('Ice Cream', 220),
    'Custard Ice Cream':        ('Ice Cream', 290),
    'Mango Ice Cream':          ('Ice Cream', 160),
}

ITEM_IMAGES = {
    'Veg Biryani': '/static/images/menu/veg/veg-biryani.jpg',
    'Aloo Paratha': '/static/images/menu/veg/aloo-paratha.jpg',
    'Dal Tadka': '/static/images/menu/veg/dal-tadka.jpg',
    'Aloo Gobi': '/static/images/menu/veg/Aloo-Gobi.jpg',
    'Pani Puri': '/static/images/menu/street-chaat/pani-puri.jpg',
    'Samosa': '/static/images/menu/street-chaat/samosa.jpg',
    'Missal Pav': '/static/images/menu/street-chaat/missal-pav.jpg',
    'Chole Bhature': '/static/images/menu/street-chaat/chole-bhature.jpg',
    'Paneer Tikha': '/static/images/menu/gym/High Protein/Paneer-Tikha.jpg',
    'Palak Paneer': '/static/images/menu/gym/High Protein/Palak-Paneer.jpg',
    'Rajma Chawal': '/static/images/menu/gym/High Protein/Rajma-Chawal.jpg',
    'Avocado Toast': '/static/images/menu/gym/High Protein/avocado-toast.jpg',
    'Gajar Halwa': '/static/images/menu/desserts and icream/Deserts/gajar-halwa.jpg',
    'Cow milk Kheer': '/static/images/menu/desserts and icream/Deserts/kheer.jpg',
    'Dryfruit Barfi': '/static/images/menu/desserts and icream/Deserts/dryfruit-barfi.jpg',
    'Gulab Jamum': '/static/images/menu/desserts and icream/Deserts/gulab-jamun.jpg',
    'Vanilla Ice Cream': '/static/images/menu/desserts and icream/Iceream/vanilla-ice-cream.png',
    'Dryfruit Ice Cream': '/static/images/menu/desserts and icream/Iceream/dryfruit-icecream.jpg',
    'Custard Ice Cream': '/static/images/menu/desserts and icream/Iceream/custard-icecream.jpg',
    'Mango Ice Cream': '/static/images/menu/desserts and icream/Iceream/mango-icecream.jpg',
}

def get_item_image(item_name):
    return ITEM_IMAGES.get(item_name, '/static/images/home/logo.jpg')

def get_admin_usernames():
    raw = os.getenv('ADMIN_USERNAMES', 'admin')
    return {u.strip().lower() for u in raw.split(',') if u.strip()}

def is_admin_username(username):
    return (username or '').strip().lower() in get_admin_usernames()

@app.context_processor
def inject_cart_count():
    if session.get('user_id'):
        count = CartItem.query.filter_by(user_id=session['user_id']).with_entities(
            db.func.sum(CartItem.quantity)
        ).scalar() or 0
        return {'cart_count': int(count)}
    return {'cart_count': 0}

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login to access this page.', 'error')
            return redirect(url_for('auth_login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('is_admin'):
            flash('Admin access required.', 'error')
            return redirect(url_for('home'))
        return f(*args, **kwargs)
    return decorated_function

# ── Page Routes ──────────────────────────────────────────────────────────────

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/desserts')
def desserts():
    return render_template('desserts.html')

@app.route('/ice-cream')
def ice_cream():
    return render_template('ice-cream.html')

@app.route('/Dessert-Icream')
def dessert_icecream():
    return render_template('Dessert-Icream.html')

@app.route('/gym-food')
def gym_food():
    return render_template('gym-food.html')

@app.route('/gym-protein')
def gym_protein():
    return render_template('gym-protein.html')

@app.route('/gym-detox')
def gym_detox():
    return render_template('gym-detox.html')

@app.route('/gym-shakes')
def gym_shakes():
    return render_template('gym-shakes.html')

@app.route('/street-chaat')
def street_chaat():
    return render_template('street-chaat.html')

@app.route('/veg')
def veg():
    return render_template('veg.html')

@app.route('/cart')
@login_required
def cart():
    user_id = session.get('user_id')
    cart_items = CartItem.query.filter_by(user_id=user_id).all()
    total = sum(item.get_total() for item in cart_items)
    return render_template('cart.html', cart_items=cart_items, total=total, get_item_image=get_item_image)

# ── Auth Routes ───────────────────────────────────────────────────────────────

@app.route('/register', methods=['GET', 'POST'])
def auth_register():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')

        if not all([username, password, confirm_password]):
            flash('All fields are required.', 'error')
            return render_template('auth/register.html')

        if password != confirm_password:
            flash('Passwords do not match.', 'error')
            return render_template('auth/register.html')

        if len(password) < 6:
            flash('Password must be at least 6 characters long.', 'error')
            return render_template('auth/register.html')

        if is_admin_username(username):
            flash('This username is reserved.', 'error')
            return render_template('auth/register.html')

        if User.query.filter_by(email=username).first():
            flash('Username already taken. Please choose another.', 'error')
            return render_template('auth/register.html')

        try:
            new_user = User(name=username, email=username, is_verified=True)
            new_user.set_password(password)
            db.session.add(new_user)
            db.session.commit()
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('auth_login'))
        except Exception:
            db.session.rollback()
            flash('Registration failed. Please try again.', 'error')

    return render_template('auth/register.html')

@app.route('/login')
def login():
    return redirect(url_for('auth_login'))

@app.route('/auth/login', methods=['GET', 'POST'])
def auth_login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        if not username or not password:
            flash('Please enter both username and password.', 'error')
            return render_template('auth/login.html')

        user = User.query.filter_by(email=username).first()

        if user and user.check_password(password):
            if not user.is_verified:
                flash('Your account is blocked. Contact admin.', 'error')
                return render_template('auth/login.html')

            session['user_id'] = user.id
            session['user_name'] = user.name
            session['user_email'] = user.email
            session['is_admin'] = is_admin_username(user.email)
            session.permanent = bool(request.form.get('remember'))

            flash(f'Welcome back, {user.name}!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Invalid username or password.', 'error')

    return render_template('auth/login.html')

@app.route('/logout')
def auth_logout():
    session.clear()
    flash('You have been logged out successfully.', 'success')
    return redirect(url_for('home'))

# ── Cart Routes ───────────────────────────────────────────────────────────────

@app.route('/add-to-cart', methods=['POST'])
@login_required
def add_to_cart():
    user_id = session.get('user_id')
    item_name = request.form.get('item_name', '').strip()

    # Server-side price lookup — prevents price tampering from form
    menu_entry = MENU_ITEMS.get(item_name)
    if not menu_entry:
        flash('Invalid item.', 'error')
        return redirect(request.referrer or url_for('home'))

    category, item_price = menu_entry
    quantity = max(1, int(request.form.get('quantity', 1)))

    try:
        existing_item = CartItem.query.filter_by(user_id=user_id, item_name=item_name).first()
        if existing_item:
            existing_item.quantity += quantity
        else:
            db.session.add(CartItem(
                user_id=user_id,
                item_name=item_name,
                item_price=item_price,
                quantity=quantity,
                category=category
            ))
        db.session.commit()
        flash(f'{item_name} added to cart!', 'success')
    except Exception:
        db.session.rollback()
        flash('Could not add item to cart. Please try again.', 'error')

    return redirect(request.referrer or url_for('home'))

@app.route('/update-cart/<int:item_id>', methods=['POST'])
@login_required
def update_cart(item_id):
    user_id = session.get('user_id')
    cart_item = CartItem.query.filter_by(id=item_id, user_id=user_id).first()

    if cart_item:
        try:
            quantity = int(request.form.get('quantity', 1))
            if quantity > 0:
                cart_item.quantity = quantity
            else:
                db.session.delete(cart_item)
            db.session.commit()
            flash('Cart updated!', 'success')
        except Exception:
            db.session.rollback()
            flash('Could not update cart.', 'error')

    return redirect(url_for('cart'))

@app.route('/remove-from-cart/<int:item_id>', methods=['POST'])
@login_required
def remove_from_cart(item_id):
    user_id = session.get('user_id')
    cart_item = CartItem.query.filter_by(id=item_id, user_id=user_id).first()

    if cart_item:
        try:
            db.session.delete(cart_item)
            db.session.commit()
            flash('Item removed from cart!', 'success')
        except Exception:
            db.session.rollback()
            flash('Could not remove item.', 'error')

    return redirect(url_for('cart'))

@app.route('/clear-cart', methods=['POST'])
@login_required
def clear_cart():
    user_id = session.get('user_id')
    try:
        CartItem.query.filter_by(user_id=user_id).delete()
        db.session.commit()
        flash('Cart cleared!', 'success')
    except Exception:
        db.session.rollback()
        flash('Could not clear cart.', 'error')
    return redirect(url_for('cart'))

# ── Order Routes ──────────────────────────────────────────────────────────────

@app.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    user_id = session.get('user_id')
    cart_items = CartItem.query.filter_by(user_id=user_id).all()

    if not cart_items:
        flash('Your cart is empty!', 'error')
        return redirect(url_for('cart'))

    if request.method == 'POST':
        delivery_address = request.form.get('delivery_address', '').strip()
        phone_number = request.form.get('phone_number', '').strip()

        if not delivery_address or not phone_number:
            flash('Please provide delivery address and phone number.', 'error')
            return render_template('checkout.html', cart_items=cart_items,
                                   total=sum(i.get_total() for i in cart_items))

        try:
            # Recalculate total server-side for integrity
            total_amount = sum(item.get_total() for item in cart_items)

            new_order = Order(
                user_id=user_id,
                total_amount=total_amount,
                delivery_address=delivery_address,
                phone_number=phone_number,
                status='Pending'
            )
            db.session.add(new_order)
            db.session.flush()  # get new_order.id before commit

            for cart_item in cart_items:
                db.session.add(OrderItem(
                    order_id=new_order.id,
                    item_name=cart_item.item_name,
                    item_price=cart_item.item_price,
                    quantity=cart_item.quantity,
                    category=cart_item.category
                ))

            # Clear cart in same transaction — atomic with order creation
            CartItem.query.filter_by(user_id=user_id).delete()
            db.session.commit()

            flash(f'Order placed successfully! Order ID: {new_order.id}', 'success')
            return redirect(url_for('order_details', order_id=new_order.id))
        except Exception:
            db.session.rollback()
            flash('Order could not be placed. Please try again.', 'error')

    total = sum(item.get_total() for item in cart_items)
    return render_template('checkout.html', cart_items=cart_items, total=total)

@app.route('/my-orders')
@login_required
def my_orders():
    user_id = session.get('user_id')
    orders = Order.query.filter_by(user_id=user_id).order_by(Order.created_at.desc()).all()
    return render_template('my_orders.html', orders=orders)

@app.route('/order/<int:order_id>')
@login_required
def order_details(order_id):
    user_id = session.get('user_id')
    order = Order.query.filter_by(id=order_id, user_id=user_id).first()

    if not order:
        flash('Order not found!', 'error')
        return redirect(url_for('my_orders'))

    return render_template('order_details.html', order=order)

@app.route('/cancel-order/<int:order_id>', methods=['POST'])
@login_required
def cancel_order(order_id):
    user_id = session.get('user_id')
    order = Order.query.filter_by(id=order_id, user_id=user_id).first()

    if not order:
        flash('Order not found!', 'error')
    elif order.status != 'Pending':
        flash('Only pending orders can be cancelled.', 'error')
    else:
        try:
            order.status = 'Cancelled'
            db.session.commit()
            flash('Order cancelled successfully!', 'success')
        except Exception:
            db.session.rollback()
            flash('Could not cancel order. Please try again.', 'error')

    return redirect(url_for('my_orders'))

# ── Admin Routes ──────────────────────────────────────────────────────────────

@app.route('/admin')
@login_required
@admin_required
def admin_panel():
    users_count = User.query.count()
    active_users_count = User.query.filter_by(is_verified=True).count()
    blocked_users_count = User.query.filter_by(is_verified=False).count()
    orders_count = Order.query.count()
    pending_count = Order.query.filter_by(status='Pending').count()
    total_revenue = db.session.query(
        db.func.coalesce(db.func.sum(Order.total_amount), 0)
    ).filter(Order.status != 'Cancelled').scalar()
    carts_count = CartItem.query.count()

    return render_template(
        'admin_panel.html',
        users_count=users_count,
        active_users_count=active_users_count,
        blocked_users_count=blocked_users_count,
        orders_count=orders_count,
        pending_count=pending_count,
        total_revenue=total_revenue,
        carts_count=carts_count
    )

@app.route('/admin/users')
@login_required
@admin_required
def admin_users():
    users = User.query.order_by(User.created_at.desc()).all()
    return render_template('admin_users.html', users=users)

@app.route('/admin/orders')
@login_required
@admin_required
def admin_orders():
    orders = Order.query.order_by(Order.created_at.desc()).all()
    return render_template('admin_orders.html', orders=orders)

@app.route('/admin/orders/<int:order_id>/status', methods=['POST'])
@login_required
@admin_required
def admin_update_order_status(order_id):
    valid_statuses = {'Pending', 'Confirmed', 'Delivered', 'Cancelled'}
    new_status = request.form.get('status', '').strip().title()
    order = Order.query.get(order_id)

    if not order:
        flash('Order not found.', 'error')
        return redirect(url_for('admin_orders'))

    if new_status not in valid_statuses:
        flash('Invalid status.', 'error')
        return redirect(url_for('admin_orders'))

    try:
        order.status = new_status
        db.session.commit()
        flash(f'Order #{order.id} updated to {new_status}.', 'success')
    except Exception:
        db.session.rollback()
        flash('Could not update order status.', 'error')

    return redirect(url_for('admin_orders'))

@app.route('/admin/users/<int:user_id>/toggle-ban', methods=['POST'])
@login_required
@admin_required
def admin_toggle_ban_user(user_id):
    user = User.query.get(user_id)
    if not user:
        flash('User not found.', 'error')
        return redirect(url_for('admin_users'))

    if user.id == session.get('user_id'):
        flash('You cannot ban/unban your own account.', 'error')
        return redirect(url_for('admin_users'))

    try:
        user.is_verified = not user.is_verified
        db.session.commit()
        state = 'unblocked' if user.is_verified else 'blocked'
        flash(f'User {user.name} {state}.', 'success')
    except Exception:
        db.session.rollback()
        flash('Could not update user status.', 'error')

    return redirect(url_for('admin_users'))

@app.route('/admin/users/<int:user_id>/delete', methods=['POST'])
@login_required
@admin_required
def admin_delete_user(user_id):
    user = User.query.get(user_id)
    if not user:
        flash('User not found.', 'error')
        return redirect(url_for('admin_users'))

    if user.id == session.get('user_id'):
        flash('You cannot delete your own account.', 'error')
        return redirect(url_for('admin_users'))

    try:
        # cascade='all, delete-orphan' on Order.order_items handles OrderItems automatically
        Order.query.filter_by(user_id=user.id).delete(synchronize_session=False)
        CartItem.query.filter_by(user_id=user.id).delete(synchronize_session=False)
        db.session.delete(user)
        db.session.commit()
        flash('User deleted successfully.', 'success')
    except Exception:
        db.session.rollback()
        flash('Could not delete user.', 'error')

    return redirect(url_for('admin_users'))

@app.route('/temp-setup-admin-2025')
def temp_setup_admin():
    admin = User.query.filter_by(email='admin').first()
    if admin:
        return 'Admin already exists!'
    new_admin = User(name='admin', email='admin', is_verified=True)
    new_admin.set_password('admin123')
    db.session.add(new_admin)
    db.session.commit()
    return 'Admin user created! Username: admin, Password: admin123. DELETE THIS ROUTE NOW!'

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    debug_mode = os.getenv('DEBUG', 'False').lower() == 'true'
    app.run(debug=debug_mode)
