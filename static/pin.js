function pinThread(thread_id, pin_id) {
    let target = document.getElementById(pin_id);
    let pinned = target.dataset.isPinned === 'true';

    fetch(`/pin/${thread_id}`, {method: 'POST'})
    .then(response => response.json()) 
    .then(data => console.log(data)) 
    .catch(error => console.error(error));

    if (pinned) {
        target.style.color = '#9e9e9e';
    } else {
        target.style.color = '#1c1c1c';
    }
    target.dataset.isPinned = `${!pinned}`;
}