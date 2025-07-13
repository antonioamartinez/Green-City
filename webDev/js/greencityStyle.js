// street1.jpg - https://wpra.net/1981/01/01/save-the-trees-and-open-spaces/
// street2.jpg, street3.jpg - https://www.altaonline.com/culture/art/a60924832/southern-california-palm-citrus-trees-climate-change/


function createCircles(){
        
    const layer = document.getElementById('background-layer');
    const section = layer.parentElement;
    const sectionWidth = section.offsetWidth;
    const sectionHeight = section.offsetHeight;

    const sizes = [0.2, 0.8, 0.4, 0.3, 0.4, 0.3]; // 50%, 25%, 10%
    const hightPos = [0.04, 0.1, 0.2, 0.3, 1, 1.3];
    const widthPos = [0.01, 0.02, 0.5, 1, 0.6, 0.05];
    const numCircles = 6;
    const sections = 6;

    for (let i = 0; i < numCircles; i++) {
        const sizeFactor = sizes[i];
        const pxSize = sectionWidth * sizeFactor;

        const circle = document.createElement('div');
        circle.classList.add('circle');
        circle.style.width = pxSize + 'px';
        circle.style.height = pxSize + 'px';

        //const x =  (maxX - minX) + minX;
        const x = widthPos[i] * sectionWidth;
        const y = hightPos[i] * sectionHeight;

        circle.style.left = x + 'px';
        circle.style.top = y + 'px';

        layer.appendChild(circle);
    }
}

function getBlock(hight, yPos){
    const line = document.createElement("div");
    line.className = "verticleBlock";
    line.style.height = hight;
    line.style.top = yPos;
    document.body.appendChild(line);
}

document.addEventListener('DOMContentLoaded', () => {
    const logo   = document.getElementById('logo');
    const app = document.getElementById('app');
    const initPage = document.getElementById('page-top');


    // ‑‑‑ Observe when the trigger section enters the viewport ‑‑‑
    function onScroll() {

        // check top page for logo change
        const toprect = initPage.getBoundingClientRect();
        const newSrc = 'assets/img/logo.png'; 
        const topSrc = 'assets/img/logoTop.png'
        const topViewport = toprect.top < -15 ; 

        if (topViewport)  {          // section’s top has reached viewport top
            logo.src = newSrc;
            logo.classList.add('topPage');
        } else {
            logo.src = topSrc;
            logo.classList.remove('topPage');

        }

        // check app page for logo change
        const rect = app.getBoundingClientRect();
        const inViewport = rect.top <= 150 && rect.bottom >  150; // section still intersects the viewport

        if (inViewport)  {          // section’s top has reached viewport top
            logo.classList.add('shrunk');
        } else {
            logo.classList.remove('shrunk');
        }
        
        
    }

    window.addEventListener('scroll', onScroll, { passive: true });
    onScroll();
});