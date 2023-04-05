# Stock-Home
STOCK-HOME is a web application that provides users with real-time stock prices and allows them to simulate buying and selling stocks using virtual money. This project is built using Python, Flask, and the IEX API.

## Features
User registration and login
Real-time stock prices using the IEX API
Simulation of buying and selling stocks using virtual money
Transaction details stored in user accounts

## Installation
To run the STOCK-HOME application locally, you'll need to follow these steps:

Clone the repository: git clone https://github.com/rajsanu/Stock-Home.git
Navigate to the project directory: cd STOCK-HOME
Install the required packages: pip install -r requirements.txt
Obtain an API key from IEX API: iexcloud.io/cloud-login#/register/
Add the API key to your environment variables: export API_KEY="YOUR-API-KEY"
Run the application: python app.py

## Usage
Once the application is running, you can access it at http://localhost:5000/ in your web browser. You can register a new user account by clicking on the "Register" link on the navigation bar. After registering, you can log in using your username and password.

Once you register, you will be awarded a certain amount of virtual(fake) money using which buying and selling of stocks can be simulated. The home page will display a number of options in the navigation bar. By selecting "Quote" option, you can view the stock's real time price by entering the stock symbol. By clicking on "Sell", you will be able to simulate the selling of stocks that you have bought at stock's current price. You can also buy stocks with the virtual money present in your account. You can view the details of all your past transactions by clicking on "records" symbol. And, by clicking "logout", you can log out from the website

## Contributing
If you'd like to contribute to this project, please fork the repository and create a pull request with your changes.

## License
This project is licensed under the MIT License.
