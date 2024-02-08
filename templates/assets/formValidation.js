// formValidation.js///Function to validate numerical input within a range
function validateRangeInput(value, min, max) {
    return value >= min && value <= max;
}

// Function to serialize form data
function serializeFormData(form) {
    const formData = new FormData(form);
    const data = {};

    for (const [key, value] of formData.entries()) {
        data[key] = value;
    }

    return data;
}

// Function to validate form data
function validateFormData(formId) {
    let isValid = true;
    let errorMessage = '';

    if (formId === '1') {
        const minBitrate = parseInt(document.getElementById('voice_min_bitrate').value, 10);
        const maxBitrate = parseInt(document.getElementById('voice_max_bitrate').value, 10);
        if (!validateRangeInput(minBitrate, 8, 16) || !validateRangeInput(maxBitrate, 8, 16)) {
            errorMessage = 'Bitrate for voice traffic must be between 8 and 16 kbps.';
            isValid = false;
        }
    } else if (formId === '2') {
        const minStreams = parseInt(document.getElementById('video_min_streams').value, 10);
        const maxStreams = parseInt(document.getElementById('video_max_streams').value, 10);
        const minBitrate = parseInt(document.getElementById('video_min_bitrate').value, 10);
        const maxBitrate = parseInt(document.getElementById('video_max_bitrate').value, 10);
        const jitter = parseFloat(document.getElementById('video_jitter').value); // Assuming there is an input with id 'video_jitter'
        if (!validateRangeInput(minStreams, 1, 5) || !validateRangeInput(maxStreams, 1, 5) ||
            !validateRangeInput(minBitrate, 3, 8) || !validateRangeInput(maxBitrate, 3, 8) ||
            isNaN(jitter)) { // Add validation for jitter if needed
            errorMessage = 'Number of streams must be between 1 and 5, bitrate must be between 3 and 8 Mbps, and jitter must be a valid number.';
            isValid = false;
        }
    
    } else if (formId === '3') {
        const minBitrate = parseInt(document.getElementById('gaming_min_bitrate').value, 10);
        const maxBitrate = parseInt(document.getElementById('gaming_max_bitrate').value, 10);
        const jitter = parseFloat(document.getElementById('gaming_jitter').value);
        const delay = parseFloat(document.getElementById('gaming_delay').value);
        const packetLossRate = parseFloat(document.getElementById('gaming_packet_loss_rate').value);

        if (!validateRangeInput(minBitrate, 30, 70)) {
            errorMessage = 'Minimum bitrate for gaming traffic must be between 30 and 70 Mbps.';
            isValid = false;
        }
        if (!validateRangeInput(maxBitrate, 30, 70)) {
            errorMessage += errorMessage ? '\n' : '';
            errorMessage += 'Maximum bitrate for gaming traffic must be between 30 and 70 Mbps.';
            isValid = false;
        }
        if (!validateRangeInput(jitter, 0, 100)) {
            errorMessage += errorMessage ? '\n' : '';
            errorMessage += 'Jitter for gaming traffic must be between 0 and 100 ms.';
            isValid = false;
        }
        if (!validateRangeInput(delay, 0, 1000)) {
            errorMessage += errorMessage ? '\n' : '';
            errorMessage += 'Delay for gaming traffic must be between 0 and 1000 ms.';
            isValid = false;
        }
        if (!validateRangeInput(packetLossRate, 0, 1)) {
            errorMessage += errorMessage ? '\n' : '';
            errorMessage += 'Packet loss rate for gaming traffic must be between 0 and 1.';
            isValid = false;
        }
    
    } else if (formId === '4') {
        const minPacketSize = parseInt(document.getElementById('iot_min_packet_size').value, 10);
        const maxPacketSize = parseInt(document.getElementById('iot_max_packet_size').value, 10);
        const minInterval = parseInt(document.getElementById('iot_min_interval').value, 10);
        const maxInterval = parseInt(document.getElementById('iot_max_interval').value, 10);
        if (!validateRangeInput(minPacketSize, 20, 1500) || !validateRangeInput(maxPacketSize, 20, 1500)) {
            errorMessage = 'Packet size for IoT traffic must be between 20 and 1500 bytes.';
            isValid = false;
        }
        if (!validateRangeInput(minInterval, 1, 60) || !validateRangeInput(maxInterval, 1, 60)) {
            errorMessage += errorMessage ? '\n' : '';
            errorMessage += 'Interval for IoT traffic must be between 1 and 60 seconds.';
            isValid = false;
        }
    } else if (formId === '5') {
        const minBitrate = parseInt(document.getElementById('data_min_bitrate').value, 10);
        const maxBitrate = parseInt(document.getElementById('data_max_bitrate').value, 10);
        const minInterval = parseInt(document.getElementById('data_min_interval').value, 10);
        const maxInterval = parseInt(document.getElementById('data_max_interval').value, 10);
        // Add any additional validations if the backend expects more parameters
        if (!validateRangeInput(minBitrate, 10, 1000) || !validateRangeInput(maxBitrate, 10, 1000)) {
            errorMessage = 'Bitrate for data traffic must be between 10 and 1000 Mbps.';
            isValid = false;
        }
        if (!validateRangeInput(minInterval, 1, 60) || !validateRangeInput(maxInterval, 1, 60)) {
            errorMessage += errorMessage ? '\n' : '';
            errorMessage += 'Interval for data traffic must be between 1 and 60 seconds.';
            isValid = false;
        }
    }


    return { isValid, errorMessage };
}
    
// Function to handle form submission
function handleFormSubmit(event) {
    event.preventDefault();
    const form = event.target;
    const formId = form.id;
    const validation = validateFormData(formId);

    if (!validation.isValid) {
        alert(validation.errorMessage);
        return;
    }

    let data = serializeFormData(form);

     // Adjust the keys for gaming traffic form
    if (formId === '3') {
        data = {
            bitrate_range: [parseInt(data.gaming_min_bitrate, 10), parseInt(data.gaming_max_bitrate, 10)],
            jitter: parseFloat(data.gaming_jitter),
            delay: parseFloat(data.gaming_delay),
            packet_loss_rate: parseFloat(data.gaming_packet_loss_rate)
        };
    }

// Log the data to the server before sending it
console.log('Data being sent to the server:', data);

// Endpoint based on the formId
const service = formId.replace('Form', '');
// Ensure the service name is formatted correctly to match the Flask route
const endpoint = `http://127.0.0.1:5000/update_${getEndpointSuffix(formId)}`;


fetch(endpoint, {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
    },
    body: JSON.stringify(data),
})
.then(response => {
    if (!response.ok) {
        throw new Error('Network response was not ok');
    }
    return response.json();
})
.then(data => {
    console.log('Success:', data);
    alert('Traffic updated successfully');
})
.catch((error) => {
    console.error('Error:', error);
    alert('Error updating traffic');
});
}

// Function to determine the endpoint suffix based on the formId
function getEndpointSuffix(formId) {
    console.log("Received formId in getEndpointSuffix:", formId);
    switch (formId) {
        case '1':
            return 'voice_traffic';
        case '2':
            return 'video_traffic';
        case '3':
            return 'gaming_traffic';
        case '4':
            return 'iot_traffic';
        case '5':
            return 'data_traffic';
        default:
            return 'unknown';
    }
}

// Attach event listeners to forms
document.addEventListener('DOMContentLoaded', function() {
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', handleFormSubmit);
    });
});