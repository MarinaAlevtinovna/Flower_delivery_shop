# Flower_delivery_shop
 Flower Delivery Shop is a Django-based web application that allows users to browse and order flowers online. Users can add flowers to their cart, proceed with checkout, and receive their orders at their desired address. It also supports Telegram notifications for order updates.

## Installation

1. Clone the repository:

    ```bash
    git clone https://github.com/yourusername/flower-delivery-shop.git
    ```

2. Navigate into the project directory:

    ```bash
    cd flower-delivery-shop
    ```

3. Create a virtual environment:

    ```bash
    python -m venv venv
    ```

4. Activate the virtual environment:
    - For Windows:

        ```bash
        .\venv\Scripts\activate
        ```

    - For MacOS/Linux:

        ```bash
        source venv/bin/activate
        ```

5. Install dependencies:

    ```bash
    pip install -r requirements.txt
    ```

6. Run migrations:

    ```bash
    python manage.py migrate
    ```

7. Run the development server:

    ```bash
    python manage.py runserver
    ```

The application will be running at [http://127.0.0.1:8000](http://127.0.0.1:8000).

