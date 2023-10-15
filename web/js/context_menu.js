const contextMenu = document.getElementById('contextMenu');
    let selectedDivID = ""
    function onSelect(e, selectedDiv){
        e.preventDefault(); // Prevent the default context menu
        
         // Get the position of the div and the size of the context menu
        const divRect = selectedDiv.getBoundingClientRect();
        const menuRect = contextMenu.getBoundingClientRect();

        // Calculate the position for the context menu
        let left = e.pageX;
        let top = e.pageY;

        // Check if the menu would go off the right edge of the screen
        width = Math.max(menuRect.width, 100)
        if (left +  width> window.innerWidth) {
            left = window.innerWidth - width;
        }

        // Check if the menu would go off the bottom edge of the screen
        if (top + menuRect.height > window.innerHeight) {
            top = window.innerHeight - menuRect.height;
        }

        contextMenu.style.display = 'block';
        contextMenu.style.left = `${left}px`;
        contextMenu.style.top = `${top}px`;
        
        selectedDiv.style.borderColor = '#3498db'; // Add your preferred blue shading color
        selectedDivID = selectedDiv.id;
        //remove shading from unselected divs
        for (const div of statusDivs){
            if (!(div.id === selectedDiv.id)){
                div.style.borderColor = 'transparent';
            }
        }
    }

    //strange function calls necessary to make border change work when text is clicked instead of background
    for (const div of statusDivs){
        div.addEventListener('contextmenu', (e) => {
            onSelect(e, div)
        });
    }

    const menuItems = contextMenu.querySelectorAll('li');

    menuItems.forEach((item) => {
        item.addEventListener('click', () => {
            alert(`Restarting `+selectedDivID);
            //cursed
            window[selectedDivID+"_restart"]();
            contextMenu.style.display = 'none'; // Hide the context menu
        });
    });

    // Hide the context menu when clicking outside of it
    document.addEventListener('click', () => {
        contextMenu.style.display = 'none';
        // Remove the shading effect from the divs
        for (const div of statusDivs){
            div.style.borderColor = 'transparent';
        }
    });