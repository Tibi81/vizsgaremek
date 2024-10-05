let updateBtns = document.getElementsByClassName('update-cart');

for (let i = 0; i < updateBtns.length; i++) {
    updateBtns[i].addEventListener('click', function() {
        var productId = this.dataset.product;
        var action = this.dataset.action;
        console.log('productId:', productId, 'Action:', action);
		
        console.log('USER:', user);  // Ellenőrizd, hogy helyes felhasználó van-e betöltve

        if (user === 'AnonymousUser') {
            alert('Kérjük, jelentkezzen be a kosár használatához!');
            // Opcionálisan átirányíthatod a felhasználót a bejelentkezési oldalra:
            // window.location.href = '/login/';
        } else {
            updateUserOrder(productId, action);
        }
    });
}

function updateUserOrder(productId, action) {
    console.log('User is authenticated, sending data...');

    const url = '/update_item/';

    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken,
        },
        body: JSON.stringify({ 'productId': productId, 'action': action })
    })
    .then((response) => {
        return response.json();
    })
    .then((data) => {
        location.reload();
    });
}

function addCookieItem(productId, action) {
    console.log('User is not authenticated');

    // Ha nem bejelentkezett a felhasználó, ne frissítsük a kosarat
    if (action === 'add') {
        alert('Kérjük, jelentkezzen be a kosár használatához!');
    }

    if (action === 'remove') {
        alert('Kérjük, jelentkezzen be a kosár használatához!');
    }
}
