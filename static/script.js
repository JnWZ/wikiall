function toggleSearchBar() {
    var searchBar = document.querySelector('.search-bar'); // Utilisez querySelector avec la classe .search-bar
    searchBar.style.display = searchBar.style.display === 'none' ? 'block' : 'none';
}

function search() {
    var searchInput = document.getElementById('search-input').value;
    // Effectuer la recherche avec la valeur de searchInput
    console.log('Recherche lancée pour : ' + searchInput);
}

// Sélectionnez l'icône de recherche
const searchIconBtn = document.getElementById('search-bar button');

// Sélectionnez la barre de recherche
const searchBar = document.querySelector('.search-bar');

// Ajoutez un écouteur d'événements pour le clic sur l'icône de recherche
searchIconBtn.addEventListener('click', function() {
    // Basculez la classe CSS pour afficher ou masquer la barre de recherche
    searchBar.classList.toggle('show');
});
