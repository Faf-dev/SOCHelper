from app import createApp, db

app = createApp()

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        print("Base de données SQLite prête")
    
    app.run(debug=True, host="0.0.0.0", port=5000)
