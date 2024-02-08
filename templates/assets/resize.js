document.addEventListener('DOMContentLoaded', function() {
    // Resize Handlers
    var isResizing = false;
    var mapContainer = document.getElementById('map-container');
    var tabsContainer = document.getElementById('tabs-container');
    var divider = document.getElementById('divider');  // Assuming there's a divider element for resizing

    divider.addEventListener('mousedown', function(e) {
        isResizing = true;
    });

    document.addEventListener('mousemove', function(e) {
        if (!isResizing) return;
        var containerOffsetTop = mapContainer.offsetTop;
        var newHeight = e.clientY - containerOffsetTop;

        mapContainer.style.height = newHeight + 'px';
        tabsContainer.style.height = 'calc(100vh - ' + newHeight + 'px)';
    });

    document.addEventListener('mouseup', function() {
        isResizing = false;
    });

    // Form Submission Handling
    var forms = ['1', '2', '3', '4', '5']; 
    forms.forEach(function(formId) {
        var form = document.getElementById(formId);
        if (form) {
            form.addEventListener('submit', function(e) {
                e.preventDefault();
                var data = serializeForm(formId);

                try {
                    validatePayload(data, formId); // Pass formId as an argument
                    sendPostRequest(formId, data);
                } catch (error) {
                    console.error('Validation Error:', error);
                    // Handle validation error (e.g., show error message to user)
                }
            });
        }
    });
});

function validatePayload(data, formId) {
    // Common validation for all forms
    if ('bitrate_range' in data && (!Array.isArray(data.bitrate_range) || data.bitrate_range.length !== 2 || data.bitrate_range.some(isNaN))) {
        throw new Error("Bitrate range must be an array of two numbers.");
    }
    if ('jitter' in data && typeof data.jitter !== 'number') {
        throw new Error("Jitter must be a number.");
    }
    if ('delay' in data && typeof data.delay !== 'number') {
        throw new Error("Delay must be a number.");
    }
    if ('packet_loss_rate' in data && typeof data.packet_loss_rate !== 'number') {
        throw new Error("Packet loss rate must be a number.");
    }

    // Specific validation for video traffic form
    if (formId === '2') {
        if (!Array.isArray(data.num_streams_range) || data.num_streams_range.length !== 2 || data.num_streams_range.some(isNaN)) {
            throw new Error("Number of streams range must be an array of two numbers.");
        }
        if (!Array.isArray(data.stream_bitrate_range) || data.stream_bitrate_range.length !== 2 || data.stream_bitrate_range.some(isNaN)) {
            throw new Error("Stream bitrate range must be an array of two numbers.");
        }
    }

    // Add additional specific validations for other forms if necessary
    // ...

    // If all validations pass, return true
    return true;
}

function serializeForm(formId) {
    var form = document.getElementById(formId);
    var elements = form.elements;
    var data = {};

    for (var i = 0; i < elements.length; i++) {
        if (elements[i].type !== 'submit') {
            data[elements[i].name] = elements[i].type === 'number' ? parseFloat(elements[i].value) : elements[i].value;
        }
    }

    // Adjusting the data structure based on the formId
    switch(formId) {
        case '3':
            data = {
                bitrate_range: [data.gaming_min_bitrate, data.gaming_max_bitrate],
                jitter: data.gaming_jitter,
                delay: data.gaming_delay,
                packet_loss_rate: data.gaming_packet_loss_rate
            };
            break;
        case '2':
            data = {
                num_streams_range: [data.video_min_streams, data.video_max_streams],
                stream_bitrate_range: [data.video_min_bitrate, data.video_max_bitrate],
                jitter: data.video_jitter,
                delay: data.video_delay,
                packet_loss_rate: data.video_packet_loss_rate
            };
            break;
        case '1':
            data = {
                bitrate_range: [data.voice_min_bitrate, data.voice_max_bitrate],
                jitter: data.voice_jitter,
                delay: data.voice_delay,
                packet_loss_rate: data.voice_packet_loss_rate
            };
            break;
        case '4':
            data = {
                packet_size_range: [data.iot_min_packet_size, data.iot_max_packet_size],
                interval_range: [data.iot_min_interval, data.iot_max_interval],
                jitter: data.iot_jitter,
                delay: data.iot_delay,
                packet_loss_rate: data.iot_packet_loss_rate
            };
            break;
        case '5':
            data = {
                bitrate_range: [data.data_min_bitrate, data.data_max_bitrate],
                interval_range: [data.data_min_interval, data.data_max_interval],
                jitter: data.data_jitter,
                delay: data.data_delay,
                packet_loss_rate: data.data_packet_loss_rate
            };
            break;
        // Add any additional form adjustments here if needed
    }

    return data;
}
// Endpoint map
const endpointMap = {
    "1": 'update_voice_traffic',
    "2": 'update_video_traffic',
    "3": 'update_game_traffic',
    "4": 'update_iot_traffic',
    "5": 'update_data_traffic',
};

// Function to send POST request
function sendPostRequest(formId, data) {
    const endpoint = `http://127.0.0.1:5000/${endpointMap[formId.toString()]}`;
    console.log("Endpoint URL:", endpoint); // Log the endpoint URL
    fetch(endpoint, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok: ' + response.statusText);
        }
        return response.json();
    })
    .then(data => {
        console.log('Success:', data);
        alert('Traffic updated successfully');
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Error updating traffic: ' + error.message);
    });
}
