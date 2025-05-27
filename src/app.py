from flask import Flask, request, jsonify
from models import db, Role, Permission, RolePermission, User, Post
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)


def create_tables():
    db.create_all()

@app.route('/')
def index():
    return {'повідомлення': 'API працює!'}, 200

# ========== Користувачі ==========

@app.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    return jsonify([{'id': u.id, 'username': u.username} for u in users])

# Реєстрація користувача
@app.route('/register', methods=['POST'])
def register_user():
    data = request.get_json()
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'помилка': 'Користувач з таким ім\'ям вже існує'}), 400

    hashed_password = generate_password_hash(data['password'])
    user = User(username=data['username'], password=hashed_password, role_id=data.get('role_id'))
    db.session.add(user)
    db.session.commit()
    return jsonify({'повідомлення': 'Реєстрація успішна', 'id': user.id}), 201

# Логін
@app.route('/login', methods=['POST'])
def login_user():
    data = request.get_json()
    user = User.query.filter_by(username=data['username']).first()
    if user and check_password_hash(user.password, data['password']):
        return jsonify({'повідомлення': 'Вхід успішний', 'користувач': {'id': user.id, 'username': user.username}})
    return jsonify({'помилка': 'Невірний логін або пароль'}), 401

# ========== Пости ==========

# Отримати всі пости
@app.route('/posts', methods=['GET'])
def get_posts():
    posts = Post.query.all()
    print(posts) 
    return jsonify([
        {'id': p.id, 'title': p.title, 'content': p.content, 'user_id': p.user_id}
        for p in posts
    ])

# Отримати пост за id
@app.route('/posts/<int:post_id>', methods=['GET'])
def get_post(post_id):
    post = Post.query.get(post_id)
    if not post:
        return jsonify({'помилка': 'Пост не знайдено'}), 404
    return jsonify({'id': post.id, 'title': post.title, 'content': post.content, 'user_id': post.user_id})

# Створити новий пост
@app.route('/posts', methods=['POST'])
def create_post():
    data = request.get_json()
    post = Post(title=data['title'], content=data['content'], user_id=data['user_id'])
    db.session.add(post)
    db.session.commit()
    return jsonify({'повідомлення': 'Пост створено', 'id': post.id}), 201

# Оновити пост
@app.route('/posts/<int:post_id>', methods=['PUT'])
def update_post(post_id):
    post = Post.query.get(post_id)
    if not post:
        return jsonify({'помилка': 'Пост не знайдено'}), 404

    data = request.get_json()
    post.title = data.get('title', post.title)
    post.content = data.get('content', post.content)
    db.session.commit()
    return jsonify({'повідомлення': 'Пост оновлено'})

# Видалити пост
@app.route('/posts/<int:post_id>', methods=['DELETE'])
def delete_post(post_id):
    post = Post.query.get(post_id)
    if not post:
        return jsonify({'помилка': 'Пост не знайдено'}), 404

    db.session.delete(post)
    db.session.commit()
    return jsonify({'повідомлення': 'Пост видалено'})


  
if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Створює всі таблиці, якщо їх ще немає
        print("✅ База даних створена")
    app.run(debug=True)