# Consensus Backend Setup Guide

This guide will walk you through setting up your Python virtual environment for the Consensus backend project.

## Step 1: Create a Virtual Environment

Open your terminal and navigate to the `consensus-backend` directory, then run:

```bash
python3 -m venv venv
```

This creates a new virtual environment in a folder named `venv`.

## Step 2: Activate the Virtual Environment

### On Mac/Linux:
```bash
source venv/bin/activate
```

### On Windows:
```bash
venv\Scripts\activate
```

After activation, you should see `(venv)` at the beginning of your terminal prompt.

## Step 3: Install Dependencies

With your virtual environment activated, install the required packages:

```bash
pip install -r requirements.txt
```

This will install all the dependencies listed in `requirements.txt` (Flask, Flask-SocketIO, python-dotenv, and Supabase).

## Step 4: Deactivate the Virtual Environment

When you're done working, you can deactivate the virtual environment by running:

```bash
deactivate
```

The `(venv)` prefix will disappear from your terminal prompt.

## Notes

- Always activate your virtual environment before working on the project
- Make sure you're in the `consensus-backend` directory when creating and activating the venv
- If you encounter permission errors, you may need to use `python3` instead of `python` on some systems

