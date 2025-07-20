from flask import Flask, render_template, request, redirect, url_for, session
import json, os, uuid

app = Flask(__name__)
app.secret_key = 'your_secret_key'

def load_data():
    with open('data/restaurants.json') as f:
        return json.load(f)

def load_orders():
    if not os.path.exists('data/orders.json'):
        with open('data/orders.json', 'w') as f:
            json.dump([], f)
    with open('data/orders.json') as f:
        return json.load(f)

def save_order(order):
    orders = load_orders()
    orders.append(order)
    with open('data/orders.json', 'w') as f:
        json.dump(orders, f, indent=2)

@app.route('/')
def index():
    restaurants = load_data()
    return render_template('index.html', restaurants=restaurants)

@app.route('/menu/<restaurant_id>')
def menu(restaurant_id):
    restaurants = load_data()
    restaurant = next((r for r in restaurants if r['id'] == restaurant_id), None)
    if not restaurant:
        return "Restaurant not found", 404
    return render_template('menu.html', restaurant=restaurant)

@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    item = request.form.to_dict()
    session.setdefault('cart', []).append(item)
    session.modified = True
    return redirect(url_for('cart'))

@app.route('/cart')
def cart():
    return render_template('cart.html', cart=session.get('cart', []))

@app.route('/clear_cart')
def clear_cart():
    session['cart'] = []
    return redirect(url_for('index'))

@app.route('/order', methods=['GET'])
def order():
    cart = session.get('cart', [])
    if not cart:
        return redirect(url_for('cart'))
    return render_template('order.html', cart=cart)

@app.route('/place_order', methods=['POST'])
def place_order():
    cart = session.get('cart', [])
    if not cart:
        return redirect(url_for('cart'))
    total = sum(float(item['price']) for item in cart)
    order_id = str(uuid.uuid4())[:8].upper()
    order = {
        'order_id': order_id,
        'items': cart,
        'total': total,
        'status': 'Preparing'
    }
    save_order(order)
    session.pop('cart', None)
    return render_template('order_summary.html', cart=order['items'], total=total, order_id=order_id)

@app.route('/track', methods=['GET', 'POST'])
def track():
    status = None
    if request.method == 'POST':
        order_id = request.form['order_id'].strip().upper()
        orders = load_orders()
        order = next((o for o in orders if o['order_id'] == order_id), None)
        if order:
            status = order['status']
        else:
            status = "Order ID not found"
    return render_template('track.html', status=status)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')

