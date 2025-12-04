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

function plusSlides(n) { showSlides(slideIndex + n); }
function currentSlide(n) { showSlides(n); }

function resetTimer() {
    clearTimeout(carouselTimer);
    carouselTimer = setTimeout(showSlides, 4000);
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
    if(sidebar) sidebar.classList.toggle("active");
}

function toggleSearchDrawer() {
    const drawer = document.getElementById("searchDrawer");
    const trigger = document.querySelector(".search-trigger");
    const input = document.getElementById("searchInput");
    if (!drawer) return;

    const isOpen = drawer.classList.toggle("open");
    drawer.setAttribute("aria-hidden", (!isOpen).toString());
    document.body.classList.toggle("search-open", isOpen);
    if (trigger) trigger.setAttribute("aria-expanded", isOpen.toString());
    if (isOpen && input) input.focus();
}

function closeSearchDrawer() {
    const drawer = document.getElementById("searchDrawer");
    const trigger = document.querySelector(".search-trigger");
    if (!drawer) return;

    drawer.classList.remove("open");
    drawer.setAttribute("aria-hidden", "true");
    document.body.classList.remove("search-open");
    if (trigger) trigger.setAttribute("aria-expanded", "false");
}

function shareNews(url) {
    if (navigator.share) {
        navigator.share({ title: 'Notícia JC', url: url }).catch(console.error);
    } else {
        navigator.clipboard.writeText(url).then(() => {
            alert('Link copiado!');
        }, () => {
            alert('Link: ' + url);
        });
    }
}

async function fetchCurrency() {
    try {
        const response = await fetch('https://economia.awesomeapi.com.br/last/USD-BRL,EUR-BRL');
        const data = await response.json();
        const usd = parseFloat(data.USDBRL.bid).toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
        const eur = parseFloat(data.EURBRL.bid).toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
        
        const dItem = document.getElementById('dolar-item');
        const eItem = document.getElementById('euro-item');
        if(dItem) dItem.innerHTML = `<strong>Dólar</strong> ${usd}`;
        if(eItem) eItem.innerHTML = `<strong>Euro</strong> ${eur}`;
    } catch (e) { console.error(e); }
}

async function fetchMegaSena() {
    try {
        const response = await fetch('https://loteriascaixa-api.herokuapp.com/api/megasena/latest');
        const data = await response.json();
        const conc = document.getElementById('mega-concurso');
        const list = document.getElementById('mega-numeros');
        
        if(conc) conc.innerText = `N° ${data.concurso}`;
        if(list) {
            list.innerHTML = '';
            data.dezenas.forEach(num => {
                const li = document.createElement('li');
                li.innerText = num;
                list.appendChild(li);
            });
        }
    } catch (e) { console.error(e); }
}

async function fetchWeather() {
    try {
        const url = "https://api.open-meteo.com/v1/forecast?latitude=-8.05&longitude=-34.88&current=temperature_2m&daily=temperature_2m_max,temperature_2m_min&timezone=America%2FSao_Paulo";
        const response = await fetch(url);
        const data = await response.json();
        
        const atual = Math.round(data.current.temperature_2m);
        const max = Math.round(data.daily.temperature_2m_max[0]);
        const min = Math.round(data.daily.temperature_2m_min[0]);
        
        const wDiv = document.getElementById('weather-dados');
        if(wDiv) {
            wDiv.innerHTML = `
                <div class="temp-destaque">${atual}°C</div>
                <div class="temp-info">
                    <span>Máx: ${max}°</span>
                    <span>Mín: ${min}°</span>
                </div>
            `;
            wDiv.classList.remove('loading');
        }
    } catch (e) { console.error(e); }
}
async function fetchTides() {
    try {
        const url = "https://marine-api.open-meteo.com/v1/marine?latitude=-8.05&longitude=-34.88&daily=tide_high,tide_low&timezone=America%Recife&forecast_days=1";
        
        const response = await fetch(url);
        const data = await response.json();
        
        let eventos = [];

        if (data.daily && data.daily.tide_high) {
            data.daily.tide_high.forEach(t => {
                if(t) eventos.push({ time: t, type: 'Alta', icon: '▲', class: 'mare-up' });
            });
        }
        
        if (data.daily && data.daily.tide_low) {
            data.daily.tide_low.forEach(t => {
                if(t) eventos.push({ time: t, type: 'Baixa', icon: '▼', class: 'mare-down' });
            });
        }

        eventos.sort((a, b) => new Date(a.time) - new Date(b.time));

        let html = '';
        eventos.forEach(ev => {
            const dateObj = new Date(ev.time);
            const hora = dateObj.toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' });
            
            html += `<div class="mare-row ${ev.class}"><span>${ev.icon} ${ev.type}</span><strong>${hora}</strong></div>`;
        });

        const mDiv = document.getElementById('mare-dados');
        if(mDiv) {
            if (eventos.length > 0) {
                mDiv.innerHTML = html;
            } else {
                mDiv.innerHTML = '<span style="font-size:12px">Sem dados hoje</span>';
            }
            mDiv.classList.remove('loading');
        }
    } catch (e) { 
        console.error("Erro Maré:", e);
        const mDiv = document.getElementById('mare-dados');
        if(mDiv) {
            mDiv.innerHTML = '<span style="font-size:12px">Indisponível</span>';
            mDiv.classList.remove('loading');
        }
    }
}

document.addEventListener('DOMContentLoaded', () => {
    carouselTimer = setTimeout(showSlides, 4000);

    const searchForm = document.querySelector(".search-form");
    if (searchForm) {
        searchForm.addEventListener("submit", () => {
            closeSearchDrawer();
        });
    }

    fetchCurrency();
    fetchMegaSena();
    fetchWeather();
    fetchTides();
});

document.addEventListener("keydown", (event) => {
    if (event.key === "Escape") closeSearchDrawer();
});