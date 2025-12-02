# Deploying the Bot on cPanel

Follow these steps to deploy the Telegram bot on a cPanel server using the Python App feature.

## 1. Create the Application

1.  Log in to your cPanel account.
2.  Navigate to the **Setup Python App** page.
3.  Click **Create Application** to open the application setup form.

## 2. Configure the Application

Fill out the form with the following settings:

*   **Python version**: Choose a Python 3.x version (e.g., 3.9).
*   **Application root**: Enter the directory where you have uploaded the bot's files (e.g., `/home/your_username/telegram-bot`).
*   **Application URL**: This will be the public URL for your bot's web interface.
*   **Application startup file**: Set this to `passenger_wsgi.py`.
*   **Application Entry point**: Leave this field blank.

Once the application is created, cPanel will provide a command to install the dependencies. Copy and run this command in the terminal.

## 3. Set Environment Variables

You will need to set the following environment variables in the cPanel interface:

*   `API_ID`: Your Telegram API ID.
*   `API_HASH`: Your Telegram API hash.
*   `BOT_TOKEN`: Your bot's token.
*   `PASSENGER_APP_ENV`: Set this to `production`.

Add any other required environment variables for your bot's configuration.

## 4. Start the Application

After configuring the environment variables, restart the application from the cPanel interface. Your bot should now be running.
