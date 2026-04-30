const { Client, LocalAuth, MessageMedia } = require('whatsapp-web.js');
const express = require('express');
const QRCode = require('qrcode');
const fs = require('fs');
const path = require('path');
const bodyParser = require('body-parser');

const app = express();
app.use(bodyParser.json({ limit: '50mb' }));

const port = 3000;

// Configuração de caminhos persistentes para evitar erros no Disco C
const dataRoot = process.env.LOCALAPPDATA ? path.join(process.env.LOCALAPPDATA, 'JUVICKS_DATA', 'sessions', 'whatsapp') : path.join(__dirname, '.wwebjs_auth');
if (!fs.existsSync(path.dirname(dataRoot))) {
    fs.mkdirSync(path.dirname(dataRoot), { recursive: true });
}

const QR_PATH = path.join(dataRoot, 'qr.png');
const STATUS_FILE = path.join(dataRoot, 'status.json');

let clientState = 'loading'; // loading, qr, authenticated, ready, disconnected
let userInfo = null;
let currentQr = null;

// Inicializa o cliente do WhatsApp
const client = new Client({
    authStrategy: new LocalAuth({
        dataPath: dataRoot
    }),
    webVersionCache: { 
        type: 'none' 
    },
    puppeteer: {
        headless: true, // Modo estável
        args: [
            '--no-sandbox', 
            '--disable-setuid-sandbox',
            '--disable-gpu',
            '--disable-dev-shm-usage',
            '--no-zygote'
        ]
    }
});

// Tratamento de Erros Críticos
process.on('unhandledRejection', (error) => {
    console.error('Erro detectado:', error.message);
    if (error.message.includes('Navigating frame was detached')) {
       console.log('Erro de navegação detectado. O cache do navegador local foi desativado para tentar evitar isso.');
    }
});

function updateStatus(state, user = null, qr = null) {
    clientState = state;
    userInfo = user;
    currentQr = qr;
    try {
        fs.writeFileSync(STATUS_FILE, JSON.stringify({ 
            status: state, 
            user: user, 
            qr: qr, 
            lastUpdate: new Date() 
        }));
    } catch(e) {}
}

client.on('qr', (qr) => {
    console.log('QR Code recebido, aguardando scan...');
    // Gera a imagem em Base64 diretamente no Node.js para evitar problemas de dependência no Python
    QRCode.toDataURL(qr, (err, url) => {
        if (!err && url) {
            updateStatus('qr', null, url);
        } else {
            updateStatus('qr', null, qr); // fallback para string crua se falhar
        }
    });
});

client.on('ready', async () => {
    console.log('Cliente pronto!');
    const info = client.info;
    updateStatus('ready', info.pushname || info.wid.user, null);
});

client.on('authenticated', () => {
    console.log('Autenticado com sucesso!');
    updateStatus('authenticated', null, null);
});

client.on('auth_failure', (msg) => {
    console.error('Falha na autenticação:', msg);
    updateStatus('disconnected', null, null);
});

client.on('disconnected', (reason) => {
    console.log('Desconectado:', reason);
    updateStatus('disconnected', null, null);
});

// --- API ENDPOINTS ---

app.get('/status', (req, res) => {
    res.json({ status: clientState, user: userInfo, qr: currentQr });
});

app.get('/logout', async (req, res) => {
    try {
        await client.logout();
        updateStatus('disconnected');
        res.json({ success: true });
    } catch (e) {
        res.status(500).json({ error: e.message });
    }
});

app.post('/send-message', async (req, res) => {
    const { number, message } = req.body;
    if (clientState !== 'ready') return res.status(503).json({ error: 'WhatsApp não está pronto' });
    
    try {
        const chatId = number.includes('@c.us') ? number : `${number}@c.us`;
        await client.sendMessage(chatId, message);
        res.json({ success: true });
    } catch (e) {
        res.status(500).json({ error: e.message });
    }
});

app.post('/send-pdf', async (req, res) => {
    const { number, pdf_base64, filename, caption } = req.body;
    if (clientState !== 'ready') return res.status(503).json({ error: 'WhatsApp não está pronto' });

    try {
        const chatId = number.includes('@c.us') ? number : `${number}@c.us`;
        // Limpa o base64 para garantir que não tenha prefixos ou espaços
        const cleanBase64 = pdf_base64.replace(/^data:application\/pdf;base64,/, '').trim();
        const media = new MessageMedia('application/pdf', cleanBase64, filename || 'documento.pdf');
        await client.sendMessage(chatId, media, { caption: caption || '' });
        res.json({ success: true });
    } catch (e) {
        res.status(500).json({ error: e.message });
    }
});

// Endpoint exclusivo para enviar alertas para o PRÓPRIO número do admin logado
app.post('/send-self', async (req, res) => {
    const { message } = req.body;
    if (clientState !== 'ready') return res.status(503).json({ error: 'WhatsApp não está pronto' });

    try {
        // client.info.wid._serialized é o ID do celular que escaneou o QR Code
        await client.sendMessage(client.info.wid._serialized, message);
        res.json({ success: true });
    } catch (e) {
        res.status(500).json({ error: e.message });
    }
});

// Inicia o motor
client.initialize();
app.listen(port, () => {
    console.log(`Gateway WhatsApp rodando na porta ${port}`);
    updateStatus('loading');
});
