# Animating String Diagrams

This repository contains the code used for the application hosted at https://animate-xsh5.onrender.com.

Assuming you have python3, pip, and npm, you should be able to run the application with the following commands.
You may also need to install ffmpeg, LaTeX, and PangoCairo.

## Running the back-end

```
cd server
python3 -m venv .env
pip install -r requirements.txt
python3 manage.py runserver
```

## Running the front-end

```
cd client
npm run dev
```

