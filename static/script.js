// Modal logic
document.getElementById('open-modal').onclick = function () {
    document.getElementById('info-modal').style.display = 'block';
};
document.getElementById('close-modal').onclick = function () {
    document.getElementById('info-modal').style.display = 'none';
};
document.getElementById('info-modal').onclick = function (e) {
    if (e.target === this) this.style.display = 'none';
};

// Refresh drinkers and highlight next payer
async function refreshDrinkers() {
    const [drinkersRes, nextPayerRes] = await Promise.all([
        fetch('/drinkers'),
        fetch('/next-payer')
    ]);
    if (drinkersRes.ok && nextPayerRes.ok) {
        const drinkers = await drinkersRes.json();
        const nextPayer = await nextPayerRes.json();
        const list = document.getElementById('drinker-list');
        list.innerHTML = '';
        drinkers.forEach(drinker => {
            const balance = (drinker.total_paid_into_pot - drinker.total_person_drinks_cost).toFixed(2);
            const balanceColor = balance >= 0 ? 'green' : 'red';
            const isNext = nextPayer && drinker.name === nextPayer.name;
            const li = document.createElement('li');
            li.setAttribute('data-name', drinker.name);
            li.setAttribute('data-favorite-drink-name', drinker.favorite_drink_name);
            li.setAttribute('data-favorite-drink-cost', drinker.favorite_drink_cost.toFixed(2));
            if (isNext) li.classList.add('next-to-pay');
            li.innerHTML = `<strong>${drinker.name}</strong> (Favorite: ${drinker.favorite_drink_name} – $${drinker.favorite_drink_cost.toFixed(2)})<br>
                        Paid: $${drinker.total_paid_into_pot.toFixed(2)}, Consumed: $${drinker.total_person_drinks_cost.toFixed(2)}<br>
                        <span style="font-weight:bold; color:${balanceColor};">Balance: $${balance}</span>`;
            li.addEventListener('click', function () {
                const updateForm = document.getElementById('update-drinker-form');
                updateForm.name.value = drinker.name;
                updateForm.favorite_drink_name.value = drinker.favorite_drink_name;
                updateForm.favorite_drink_cost.value = drinker.favorite_drink_cost.toFixed(2);
            });
            list.appendChild(li);
        });
    }
}

// Add click listeners to initial drinker list (for first render)
document.querySelectorAll('#drinker-list li').forEach(li => {
    li.addEventListener('click', function () {
        const updateForm = document.getElementById('update-drinker-form');
        updateForm.name.value = li.getAttribute('data-name');
        updateForm.favorite_drink_name.value = li.getAttribute('data-favorite-drink-name');
        updateForm.favorite_drink_cost.value = li.getAttribute('data-favorite-drink-cost');
    });
});

// Add Drinker
document.getElementById('add-drinker-form').onsubmit = async function (e) {
    e.preventDefault();
    const form = e.target;
    const data = {
        name: form.name.value,
        favorite_drink_name: form.favorite_drink_name.value,
        favorite_drink_cost: parseFloat(form.favorite_drink_cost.value)
    };
    const res = await fetch('/drinkers', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
    });
    const resultDiv = document.getElementById('add-drinker-result');
    if (res.ok) {
        resultDiv.innerHTML = '<span class="success">Drinker added!</span>';
        form.reset();
        refreshDrinkers();
    } else {
        const err = await res.json();
        resultDiv.innerHTML = '<span class="error">Error: ' + (err.detail || 'Unknown error') + '</span>';
    }
};

// Update Drinker
document.getElementById('update-drinker-form').onsubmit = async function (e) {
    e.preventDefault();
    const form = e.target;
    const name = form.name.value;
    const data = {};
    if (form.favorite_drink_name.value) data.favorite_drink_name = form.favorite_drink_name.value;
    if (form.favorite_drink_cost.value) data.favorite_drink_cost = parseFloat(form.favorite_drink_cost.value);

    // Get the drinker by name to find their ID
    const getRes = await fetch('/drinker/name/' + encodeURIComponent(name));
    const resultDiv = document.getElementById('update-drinker-result');
    if (!getRes.ok) {
        resultDiv.innerHTML = '<span class="error">Drinker not found.</span>';
        return;
    }
    const drinker = await getRes.json();

    // Now, send the PUT request by ID
    const res = await fetch('/drinkers/' + drinker.id, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
    });
    if (res.ok) {
        resultDiv.innerHTML = '<span class="success">Drinker updated!</span>';
        form.reset();
        refreshDrinkers();
    } else {
        const err = await res.json();
        resultDiv.innerHTML = '<span class="error">Error: ' + (err.detail || 'Unknown error') + '</span>';
    }
};

// Record Coffee Round
document.getElementById('coffee-round-form').onsubmit = async function (e) {
    e.preventDefault();
    const res = await fetch('/coffee-rounds', { method: 'POST' });
    const resultDiv = document.getElementById('coffee-round-result');
    if (res.ok) {
        const data = await res.json();
        resultDiv.innerHTML = `<span class="success">Coffee round recorded! <br><b>${data.current_round.payer_name}</b> just paid for this round.</span>`;
        refreshDrinkers();
    } else {
        const err = await res.json();
        resultDiv.innerHTML = '<span class="error">Error: ' + (err.detail || 'Unknown error') + '</span>';
    }
};

// Reset Balances
document.getElementById('reset-balances-form').onsubmit = async function (e) {
    e.preventDefault();
    const res = await fetch('/reset-balances', { method: 'POST' });
    const resultDiv = document.getElementById('reset-balances-result');
    if (res.ok) {
        const data = await res.json();
        resultDiv.innerHTML = '<span class="success">' + data.message + '</span>';
        refreshDrinkers();
    } else {
        const err = await res.json();
        resultDiv.innerHTML = '<span class="error">Error: ' + (err.detail || 'Unknown error') + '</span>';
    }
};

// Initial load
window.onload = refreshDrinkers;