let updateBtns = document.getElementsByClassName('update-cart');
let deleteBtns = document.getElementsByClassName('delete-btn'); // Törlés gombok

// Kosár frissítése
for (let i = 0; i < updateBtns.length; i++) {
    updateBtns[i].addEventListener('click', function() {
        var productId = this.dataset.product;
        var action = this.dataset.action;
        var quantityInput = document.getElementById(`quantity-${productId}`);
        var quantity = quantityInput ? parseInt(quantityInput.value) || 1 : 1; // Számra konvertálás
        console.log('productId:', productId, 'Action:', action);

        console.log('USER:', user);  // Ellenőrizd, hogy helyes felhasználó van-e betöltve

        if (user === 'AnonymousUser') {
            alert('Kérjük, jelentkezzen be a kosár használatához!');
            // Opcionálisan átirányíthatod a felhasználót a bejelentkezési oldalra:
            // window.location.href = '/login/';
        } else {
            updateUserOrder(productId, action, quantity); // Mennyiség átkonvertálva
        }
    });
}

// Törlés gombok kezelése
for (let i = 0; i < deleteBtns.length; i++) {
    deleteBtns[i].addEventListener('click', function() {
        
        var productId = this.closest('.cart-row').dataset.product;
        var action = 'delete'; // Törlés akció

        if (user === 'AnonymousUser') {
            alert('Kérjük, jelentkezzen be a kosár használatához!');
        } else {
            updateUserOrder(productId, action);
        }
    });
}

function updateUserOrder(productId, action, quantity) {
    console.log('User is authenticated, sending data...');

    const url = '/update_item/'; // Cseréld le a helyes URL-re
    

    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken,
        },
        body: JSON.stringify({ 'productId': productId, 'action': action, 'quantity': quantity })
            
    })
    
    .then((response) => {
        return response.json();
    })
    .then((data) => {
        console.log(data); // Debug info

        if (action === 'delete' && data === 'Item was deleted') {
            // Távolítsd el a sort az UI-ról
            document.querySelector(`.cart-row[data-product="${productId}"]`).remove();

            // Frissítsd a kosár összegző értékét
            const cartTotal = document.querySelector('#cart-total');
            cartTotal.innerText = (parseFloat(cartTotal.innerText) - parseFloat(data.itemTotal)).toFixed(0);

            // Frissítsd a kosár összes elemének számát
            const cartItems = document.querySelector('#cart-items');
            cartItems.innerText = parseInt(cartItems.innerText) - 1;
            alert('A termék eltávolítva a kosárból.');

        } else {
            location.reload(); // Vagy frissítheted az UI-t más módon
        }
    })
    .catch((error) => {
        console.error('Error:', error);
        alert('Hiba történt a kosár frissítésekor. Kérlek próbáld újra.');
    });
}


function addCookieItem(productId, action) {
    console.log('User is not authenticated');

    // Ha nem bejelentkezett a felhasználó, ne frissítsük a kosarat
    if (action === 'add' || action === 'remove') {
        alert('Kérjük, jelentkezzen be a kosár használatához!');
    }
}

