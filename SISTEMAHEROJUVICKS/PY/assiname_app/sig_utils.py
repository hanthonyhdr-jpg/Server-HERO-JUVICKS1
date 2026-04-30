import fitz
import os
import datetime
import io

def generate_receipt_overlay(text_data, role="CLIENT"):
    """
    Gera uma imagem (pixmap) do texto para evitar o erro de 'need font file'.
    O texto eh desenhado em um canvas interno e convertido para imagem.
    """
    # Criar um documento temporario para renderizar o texto como imagem
    temp_doc = fitz.open()
    temp_page = temp_doc.new_page(width=240, height=100)
    
    # Sanitizacao e Limpeza
    def clean(t): return str(t).encode("ascii", "ignore").decode("ascii")

    # Gerar Chave de Autenticacao (Hash Curto)
    import hashlib
    auth_key = hashlib.sha1(f"{text_data.get('id', '')}{text_data.get('ip', '')}".encode()).hexdigest()[:12].upper()

    # Dados formatados para legibilidade
    doc_name = text_data.get('original_filename', 'N/A')[:25]
    info = [
        f"{'CLIENTE' if role == 'CLIENT' else 'EMPRESA'}",
        f"AUTENT: {auth_key}",
        f"Doc: {clean(doc_name)}",
        f"Data: {datetime.datetime.now().strftime('%d/%m/%Y %H:%M')}",
        f"IP: {clean(text_data.get('ip', 'N/A'))}",
        f"Loc: {clean(text_data.get('location', 'N/A'))}",
        f"IDENT: {clean(text_data.get('mac_address', 'UID-N/A')[:18])}"
    ]
    
    y = 10
    for line in info:
        # Usamos Helvetica ou similar se disponivel, tamanho 7 para ser bem legivel
        temp_page.insert_text((10, y), line, fontsize=7.5, color=(0, 0, 0))
        y += 12
    
    # 2. SE HOUVER IMAGEM DE ASSINATURA (Visual Signature)
    visual_sig_base64 = text_data.get('visual_signature')
    if visual_sig_base64 and "," in visual_sig_base64:
        header, encoded = visual_sig_base64.split(",", 1)
        import base64
        visual_img_data = base64.b64decode(encoded)
        # Inserir no lado direito do selo
        sig_rect = fitz.Rect(120, 10, 230, 90)
        temp_page.insert_image(sig_rect, stream=visual_img_data)
    
    # Converter a pagina em imagem (PNG)
    pix = temp_page.get_pixmap()
    img_data = pix.tobytes("png")
    temp_doc.close()
    return img_data

def sign_pdf(input_pdf, output_pdf, text_data, role="CLIENT"):
    """
    Insere a assinatura como IMAGEM para burlar o erro de fontes do Windows.
    Garante validade juridica com todos os dados mecanicos (IP, Loc, Device).
    """
    try:
        doc = fitz.open(input_pdf)
        page = doc[-1]
        rect_page = page.rect
        
        width = 240
        height = 100
        margin = 35
        
        if role == "CLIENT":
            rect = fitz.Rect(margin, rect_page.height - margin - height, margin + width, rect_page.height - margin)
            color = (0, 0.4, 0.8) # Azul
        else:
            rect = fitz.Rect(rect_page.width - margin - width, rect_page.height - margin - height, rect_page.width - margin, rect_page.height - margin)
            color = (0, 0.5, 0) # Verde

        # 1. Desenhar o Box (Borda e Fundo)
        shape = page.new_shape()
        shape.draw_rect(rect)
        shape.finish(color=color, fill=(1, 1, 1), width=2, fill_opacity=1)
        shape.commit()

        # 2. Gerar o selo de texto como IMAGEM (Isso mata o erro de 'font file')
        img_data = generate_receipt_overlay(text_data, role)
        
        # 3. Inserir a imagem do texto sobre o box
        page.insert_image(rect, stream=img_data)
        
        doc.save(output_pdf)
        doc.close()
        return True
    except Exception as e:
        print(f"DEBUG Error: {str(e)}")
        try: doc.close()
        except: pass
        raise e
