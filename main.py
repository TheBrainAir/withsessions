from flask import Flask, session, redirect, url_for, jsonify, request, flash, render_template
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash
import secrets
from flask_session import Session

app = Flask(__name__)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
app.config['SECRET_KEY'] = '12640892135285634'
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

app.secret_key = secrets.token_hex(16)


class User(UserMixin):

  def __init__(self, user_id):
    self.id = user_id


# Rest of the code remains the same

users = {
    'Melvin465': generate_password_hash('Max7957Melvin'),
    'TBAADMIN': generate_password_hash('TBAADMIN'),
    'Azartniy_Bomj': generate_password_hash('Shamil2680Bomj'),
}


@login_manager.user_loader
def load_user(user_id):
  return User(user_id)


@app.route('/login', methods=['GET', 'POST'])
def login():
  if request.method == 'POST':
    username = request.form['username']
    password = request.form['password']
    if username in users and check_password_hash(users[username], password):
      user = User(username)
      login_user(user)
      return redirect(url_for('index'))
    flash('Invalid username or password', 'error')
  return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
  logout_user()
  return redirect(url_for('index'))


@app.route('/admin')
@login_required
def admin():
  if 'deposit_amount' not in session:
    session['deposit_amount'] = 0
  return render_template('admin.html',
                         slot_names=session.get('slot_names', []),
                         purchase_costs=session.get('purchase_costs', []),
                         received_per_slot=session.get('received_per_slot',
                                                       []),
                         spent=session.get('spent', 0),
                         total_received=sum(
                             session.get('received_per_slot', [])),
                         created=session.get('created', 0),
                         edited=session.get('edited', 0),
                         deposit_amount=session['deposit_amount'],
                         username=current_user.id)


@app.route('/add', methods=['POST'])
@login_required
def add():
  new_name = request.form['name']
  new_cost = request.form['cost']
  try:
    float_cost = float(new_cost)
  except ValueError:
    flash('Invalid cost value', 'error')
    return redirect(url_for('admin'))
  if 'spent' not in session:
    session['spent'] = 0
  if 'slot_names' not in session:
    session['slot_names'] = []
  if 'purchase_costs' not in session:
    session['purchase_costs'] = []
  if 'received_per_slot' not in session:
    session['received_per_slot'] = []
  if 'created' not in session:
    session['created'] = 0
  session['spent'] += float_cost
  session['slot_names'].append(new_name)
  session['purchase_costs'].append(float_cost)
  session['received_per_slot'].append(0)
  session['created'] += 1
  session.modified = True
  return redirect(url_for('admin'))


@app.route('/del/<int:index>')
@login_required
def delete(index):
  if 'slot_names' in session and 0 <= index < len(session['slot_names']):
    session['spent'] -= float(session['purchase_costs'][index])
    session['received_per_slot'].pop(index)
    del session['slot_names'][index]
    del session['purchase_costs'][index]
    session['created'] -= 1
    session.modified = True
  return redirect(url_for('admin'))


@app.route('/edit_received/<int:index>', methods=['POST'])
@login_required
def edit_received(index):
  new_received = request.form['new_received']
  if 'slot_names' in session and 0 <= index < len(
      session['slot_names']) and new_received:
    try:
      session['received_per_slot'][index] += float(new_received)
      if 'edited' not in session:
        session['edited'] = 0
      session['edited'] += 1
      session.modified = True
    except ValueError:
      flash('Invalid received value', 'error')
  return redirect(url_for('admin'))


@app.route('/view')
def viewers():
  return render_template('view.html',
                         slot_names=session.get('slot_names', []),
                         purchase_costs=session.get('purchase_costs', []),
                         received_per_slot=session.get('received_per_slot',
                                                       []),
                         spent=session.get('spent', 0),
                         total_received=sum(
                             session.get('received_per_slot', [])),
                         created=session.get('created', 0),
                         edited=session.get('edited', 0),
                         deposit_amount=session.get('deposit_amount', 0),
                         theme=session.get('theme', 'default'),
                         current_theme=session.get('current_theme', 'default'))


@app.route('/admin/update_deposit', methods=['POST'])
@login_required
def update_deposit():
  try:
    session['deposit_amount'] = float(request.form['deposit_amount'])
    session.modified = True
  except ValueError:
    flash('Invalid deposit amount', 'error')
  return redirect(url_for('admin'))


@app.route('/api/reset', methods=['POST'])
@login_required
def reset_data():
  session.pop('slot_names', None)
  session.pop('purchase_costs', None)
  session.pop('received_per_slot', None)
  session.pop('spent', None)
  session.pop('created', None)
  session.pop('edited', None)
  session.pop('deposit_amount', None)
  session.modified = True
  return redirect(url_for('admin'))


@app.route('/apply_theme', methods=['POST'])
@login_required
def apply_theme():
  data = request.get_json()
  session['current_theme'] = data.get('theme', 'default')
  session.modified = True
  return jsonify({'message': 'Theme updated successfully'}), 200


@app.route('/api/data', methods=['GET'])
def get_data():
  data = {
      'slot_names': session.get('slot_names', []),
      'purchase_costs': session.get('purchase_costs', []),
      'received_per_slot': session.get('received_per_slot', []),
      'spent': session.get('spent', 0),
      'total_received': sum(session.get('received_per_slot', [])),
      'created': session.get('created', 0),
      'edited': session.get('edited', 0),
      'deposit_amount': session.get('deposit_amount', 0)
  }
  return jsonify(data)


@app.route('/')
@login_required
def index():
  return render_template('index.html')


@app.route('/themes')
@login_required
def themes():
  return render_template('themes.html')


if __name__ == '__main__':
  app.debug = True
  app.run(host='0.0.0.0', port=81)