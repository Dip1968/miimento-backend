from app.run import app

if __name__ == "__main__":
    print("Running with uvicorn Debugger...")
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=5001)
