from App import create_app
#ENTRY POINT

app = create_app()
if __name__ == "__main__":
    app.run(debug=True)