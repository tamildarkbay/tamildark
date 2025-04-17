document.getElementById('search').addEventListener('input', function(e) {
    let searchValue = e.target.value.toLowerCase();
    let cards = document.getElementsByClassName('movie-card');
    for (let card of cards) {
        let title = card.getElementsByTagName('h3')[0].textContent.toLowerCase();
        card.style.display = title.includes(searchValue) ? '' : 'none';
    }
});