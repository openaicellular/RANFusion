document.addEventListener('DOMContentLoaded', function() {
    var isResizing = false;

    var mapContainer = document.getElementById('map-container');
    var tabsContainer = document.getElementById('tabs-container');
    var divider = document.getElementById('divider');

    divider.addEventListener('mousedown', function(e) {
        isResizing = true;
    });

    document.addEventListener('mousemove', function(e) {
        if (!isResizing) {
            return;
        }

        var containerOffsetTop = mapContainer.offsetTop;
        var newHeight = e.clientY - containerOffsetTop;

        mapContainer.style.height = newHeight + 'px';
        tabsContainer.style.height = 'calc(100vh - ' + newHeight + 'px - 30px)';
    });

    document.addEventListener('mouseup', function(e) {
        isResizing = false;
    });
});
