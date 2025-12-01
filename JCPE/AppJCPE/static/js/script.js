let slideIndex = 1;
let carouselTimer;

function showSlides(n) {
    let slides = document.getElementsByClassName("carousel-slide");
    let dots = document.getElementsByClassName("dot");

    if (slides.length === 0) return;

    if (n === undefined) { 
        slideIndex++;
    } else {
        slideIndex = n;
        resetTimer();
    }
    
    if (slideIndex > slides.length) { slideIndex = 1 }
    if (slideIndex < 1) { slideIndex = slides.length }

    for (let i = 0; i < slides.length; i++) {
        slides[i].style.display = "none";
        slides[i].classList.remove("active");
    }

    for (let i = 0; i < dots.length; i++) {
        dots[i].className = dots[i].className.replace(" active", "");
    }

    slides[slideIndex - 1].style.display = "block";
    slides[slideIndex - 1].classList.add("active");
    
    if (dots.length > 0) {
        dots[slideIndex - 1].className += " active";
    }
    
    if (n === undefined) {
        carouselTimer = setTimeout(showSlides, 4000); 
    }
}

function plusSlides(n) {
    showSlides(slideIndex + n);
}

function currentSlide(n) {
    showSlides(n);
}

function resetTimer() {
    clearTimeout(carouselTimer);
    carouselTimer = setTimeout(showSlides, 4000);
}

document.addEventListener('DOMContentLoaded', () => {
    carouselTimer = setTimeout(showSlides, 4000);

    const searchForm = document.querySelector(".search-form");
    if (searchForm) {
        searchForm.addEventListener("submit", () => {
            // fecha a gaveta para mostrar o resultado
            closeSearchDrawer();
        });
    }
});

function toggleMenu() {
    var sidebar = document.getElementById("sidebar");
    sidebar.classList.toggle("active");
}

function toggleSearchDrawer() {
    const drawer = document.getElementById("searchDrawer");
    const trigger = document.querySelector(".search-trigger");
    const input = document.getElementById("searchInput");
    if (!drawer) return;

    const isOpen = drawer.classList.toggle("open");
    drawer.setAttribute("aria-hidden", (!isOpen).toString());
    document.body.classList.toggle("search-open", isOpen);
    if (trigger) {
        trigger.setAttribute("aria-expanded", isOpen.toString());
    }
    if (isOpen && input) {
        input.focus();
    }
}

function closeSearchDrawer() {
    const drawer = document.getElementById("searchDrawer");
    const trigger = document.querySelector(".search-trigger");
    if (!drawer) return;

    drawer.classList.remove("open");
    drawer.setAttribute("aria-hidden", "true");
    document.body.classList.remove("search-open");
    if (trigger) {
        trigger.setAttribute("aria-expanded", "false");
    }
}

document.addEventListener("keydown", (event) => {
    if (event.key === "Escape") {
        closeSearchDrawer();
    }
});

function shareNews(url) {
    if (navigator.share) {
        navigator.share({
            title: 'Notícia JC',
            url: url
        }).catch(console.error);
    } else {
        navigator.clipboard.writeText(url).then(function() {
            alert('Link da notícia copiado para a área de transferência!');
        }, function(err) {
            alert('Não foi possível copiar o link. O link é: ' + url);
        });
    }
}
