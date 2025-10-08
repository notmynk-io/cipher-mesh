document.addEventListener('DOMContentLoaded', () => {
    const loginForm = document.getElementById('loginForm');
    const registerForm = document.getElementById('registerForm');
    const alertBox = document.getElementById('alertBox');

    const goRegisterLink = document.getElementById('goRegister');
    const goLoginLink = document.getElementById('goLogin');

    const loginBtn = document.getElementById('loginBtn');
    const registerBtn = document.getElementById('registerBtn');
    const connectWalletBtn = document.getElementById('connectWalletBtn');
    const walletAddressInput = document.getElementById('walletAddress');


        const API_URL = "https://ciphermesh-backend.onrender.com"; // TODO: Replace this with your actual Render backend URL

    function showAlert(msg, type) {
        alertBox.textContent = msg;
        alertBox.className = `alert alert-${type} active`;
        setTimeout(() => alertBox.classList.remove('active'), 4000);
    }

    goRegisterLink.addEventListener('click', () => {
        loginForm.classList.add('hidden');
        registerForm.classList.remove('hidden');
    });

    goLoginLink.addEventListener('click', () => {
        registerForm.classList.add('hidden');
        loginForm.classList.remove('hidden');
    });

    connectWalletBtn.addEventListener('click', async () => {
        if (typeof window.ethereum === 'undefined') {
            showAlert('Please install a wallet like MetaMask first.', 'error');
            return;
        }
        try {
            const provider = new ethers.providers.Web3Provider(window.ethereum);
            const accounts = await provider.send("eth_requestAccounts", []);
            if (accounts.length > 0) {
                walletAddressInput.value = accounts[0];
                showAlert('Wallet connected successfully!', 'success');
            }
        } catch (error) {
            showAlert('Could not get wallet address. Please try again.', 'error');
            console.error("Wallet connect error:", error);
        }
    });

    registerBtn.addEventListener('click', async () => {
        const username = document.getElementById('registerUsername').value.trim();
        const walletAddress = document.getElementById('walletAddress').value.trim();
        const publicKey = document.getElementById('publicKey').value.trim();

        if (!username || !walletAddress || !publicKey) {
            showAlert('Please fill all fields', 'error');
            return;
        }

        try {
            const response = await fetch(`${API_URL}/users/register`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ username, wallet_address: walletAddress, public_key: publicKey }),
            });

            const data = await response.json();

            if (!response.ok) {
                showAlert(data.detail, 'error');
            } else {
                showAlert('Registration successful! You can now log in.', 'success');
                registerForm.classList.add('hidden');
                loginForm.classList.remove('hidden');
            }
        } catch (error) {
            showAlert('An error occurred during registration.', 'error');
            console.error("Registration error:", error);
        }
    });

    loginBtn.addEventListener('click', async () => {
        const username = document.getElementById('loginUsername').value.trim();
        if (!username) {
            showAlert('Please enter your username', 'error');
            return;
        }

        if (typeof window.ethereum === 'undefined') {
            showAlert('Please install a wallet like MetaMask first.', 'error');
            return;
        }

        try {
            // 1. Connect to wallet and get signer
            const provider = new ethers.providers.Web3Provider(window.ethereum);
            await provider.send("eth_requestAccounts", []);
            const signer = provider.getSigner();
            const walletAddress = await signer.getAddress();

            // 2. Fetch nonce from backend
            showAlert('Fetching secure nonce...', 'info');
            const nonceResponse = await fetch(`${API_URL}/users/nonce/${username}`);
            if (!nonceResponse.ok) {
                const errorData = await nonceResponse.json();
                showAlert(`Error: ${errorData.detail}`, 'error');
                return;
            }
            const { nonce } = await nonceResponse.json();

            // 3. Sign the nonce
            showAlert('Please sign the message in your wallet.', 'info');
            const signature = await signer.signMessage(nonce);

            // 4. Send signature to backend for verification
            showAlert('Verifying signature...', 'info');
            const loginResponse = await fetch(`${API_URL}/users/login`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username, signature }),
            });

            const loginData = await loginResponse.json();

            if (!loginResponse.ok) {
                showAlert(`Login failed: ${loginData.detail}`, 'error');
            } else {
                showAlert('Login successful! Redirecting...', 'success');
                // Store session info if needed, then redirect
                localStorage.setItem('username', username);
                localStorage.setItem('walletAddress', walletAddress);
                setTimeout(() => {
                    window.location.href = 'index.html'; // Redirect to the main chat page
                }, 1500);
            }

        } catch (error) {
            showAlert('An error occurred during login.', 'error');
            console.error("Login error:", error);
        }
    });
});
