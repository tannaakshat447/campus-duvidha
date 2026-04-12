# 🚀 Hosting Guide for Render

Follow these steps to deploy your **Campus Duvidha Solver** to Render's Free Tier.

## 1. Push Code to GitHub
Ensure all your project files (including the new `render.yaml`, `.gitignore`, and updated `requirements.txt`) are pushed to your GitHub repository:
- **Repo**: `tannaakshat447/campus-duvidha-solver`

## 2. Connect to Render
1. Log in to [Render.com](https://render.com).
2. Click **New +** and select **Blueprint**.
3. Connect your GitHub repository.
4. Render will automatically detect the `render.yaml` file and configure the service.

## 3. Configure Environment Variables
In the Render dashboard, go to your service settings and ensure the following **Environment Variables** are set:
- `OPENAI_API_KEY`: Your OpenAI API key.
- `ADMIN_PIN`: The PIN for the Admin Dashboard (Default: `Admin@123`).
- `SMTP_SENDER_EMAIL`: (Optional) For email notifications.
- `SMTP_SENDER_PASSWORD`: (Optional) App password for email.

## 4. Deploy
1. Click **Apply** or **Deploy**.
2. Render will run the `buildCommand`:
   - Installs React dependencies.
   - Builds the React frontend (`dist` folder).
   - Installs Python dependencies.
3. Render will then run the `startCommand`:
   - Starts the production server using `gunicorn`.

---

## ⚠️ Important: Data Persistence (Free Tier)
Since you are using the **Free Tier**:
- The SQLite database (`campus_solver.db`) is stored on an **ephemeral disk**.
- **Every time you deploy or the app restarts** (due to inactivity), the database will return to an empty state.
- **Solution for testing**: This is perfectly fine for demos. 
- **Solution for production**: If you need permanent storage, you would need to upgrade to a **Starter plan** and add a **Persistent Disk** (~$5/mo) or connect to a free external database like **Neon DB (PostgreSQL)**.

---

## 🛠️ Local Verification (Optional)
Before pushing, you can test the production build locally:
```bash
# 1. Build frontend
cd frontend
npm install
npm run build
cd ..

# 2. Start Flask with Gunicorn (on Windows use 'waitress-serve' or just 'python server.py')
python server.py
```
