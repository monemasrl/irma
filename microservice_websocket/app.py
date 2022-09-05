from app import create_app, socketio

app = create_app(debug=True)
app.logger.info(app.url_map)

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0")
