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
});

function toggleMenu() {
    var sidebar = document.getElementById("sidebar");
    sidebar.classList.toggle("active");
}

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