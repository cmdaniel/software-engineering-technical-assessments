from server import app
import os

port: int = int(os.environ.get("PORT", 3000))

app.run(port=port, debug=True)
