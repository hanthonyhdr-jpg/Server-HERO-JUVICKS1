from fpdf import FPDF
from datetime import datetime
import base64
import os
import math
import io
import requests
from PIL import Image
from utils.agenda_fotos import foto_para_bytes

class GeradorPDF(FPDF):
    def __init__(self, empresa, cliente, id_orc, vendedor, validade, *args, **kwargs):
        self.tipo_doc = kwargs.pop('tipo_doc', 'PROPOSTA COMERCIAL')
        self.is_producao = kwargs.pop('is_producao', False)
        self.data_obra = kwargs.pop('data_obra', None)
        self.hora_obra = kwargs.pop('hora_obra', None)
        self.estilo = kwargs.pop('estilo', 'classico')
        super().__init__(*args, **kwargs)
        self.empresa = empresa
        self.cliente = cliente
        self.id_orc = id_orc
        self.vendedor = vendedor
        self.validade = validade
        self.em_tabela = False 
        self.temp_logo = f"logo_{id_orc}.png"

    def header(self):
        """Cabeçalho Automático: Repete em todas as páginas"""
        logo_height = 0
        if self.empresa.get('logo_data'):
            try:
                if not os.path.exists(self.temp_logo):
                    with open(self.temp_logo, "wb") as fh: 
                        fh.write(base64.b64decode(self.empresa['logo_data']))
                img_logo = Image.open(self.temp_logo)
                w_orig, h_orig = img_logo.size
                max_w, max_h = 50, 25
                ratio = min(max_w / w_orig, max_h / h_orig, 1.0)
                img_w = w_orig * ratio
                img_h = h_orig * ratio
                logo_height = img_h
                self.image(self.temp_logo, 10, 10, img_w, img_h)
            except: pass

        self.set_y(10)
        self.set_font("Helvetica", "B", 12)
        self.set_text_color(44, 62, 80)
        nome = self.limpar_texto(self.empresa.get('empresa_nome', 'ORÇAMENTO'))
        self.cell(0, 5, nome.upper(), ln=True, align='R')
        
        self.set_font("Helvetica", "", 8)
        self.set_text_color(100, 100, 100)
        cnpj_emp = self.empresa.get('empresa_cnpj') or self.empresa.get('cnpj', '')
        tel_emp = self.empresa.get('empresa_tel') or self.empresa.get('telefone', '')
        end_emp = self.empresa.get('empresa_end') or self.empresa.get('endereco', '')
        num_emp = self.empresa.get('empresa_num') or ''
        
        if num_emp: end_emp += f", {num_emp}"
        
        self.cell(0, 4, f"CNPJ: {cnpj_emp}", ln=True, align='R')
        self.cell(0, 4, f"Contato: {tel_emp}", ln=True, align='R')
        self.cell(0, 4, self.limpar_texto(end_emp), ln=True, align='R')
        
        y_banner = max(28, 10 + logo_height + 10)
        self.set_y(y_banner)
        self.set_fill_color(44, 62, 80)
        self.set_text_color(255, 255, 255)
        self.set_font("Helvetica", "B", 11)
        self.cell(0, 8, f"  {self.tipo_doc} Nº {self.id_orc}  |  Validade: {self.validade} dias", ln=True, fill=True)

        if self.page_no() == 1:
            self.ln(4)
            self.set_text_color(0, 0, 0)
            self.set_font("Helvetica", "B", 9)
            self.cell(100, 5, "DESTINATARIO", ln=0)
            self.cell(0, 5, "DETALHES", ln=1)
            self.set_font("Helvetica", "", 8)
            self.cell(100, 4, f"Nome: {self.limpar_texto(self.cliente.get('nome', '')).upper()}", ln=0)
            if self.is_producao and self.data_obra:
                d_inst = datetime.strptime(self.data_obra, '%Y-%m-%d').strftime('%d/%m/%Y') if '-' in self.data_obra else self.data_obra
                self.cell(0, 4, f"PREVISAO INSTALACAO: {d_inst} {self.hora_obra or ''}", ln=1)
            else:
                self.cell(0, 4, f"Data: {datetime.now().strftime('%d/%m/%Y')}", ln=1)
            
            # Endereço do Cliente
            end_cli = f"{self.cliente.get('endereco', '')}, {self.cliente.get('numero', '')}"
            if self.cliente.get('bairro'): end_cli += f" - {self.cliente.get('bairro', '')}"
            if self.cliente.get('cidade'): end_cli += f" ({self.cliente.get('cidade', '')})"
            
            self.cell(100, 4, f"Endereço: {self.limpar_texto(end_cli)}", ln=0)
            if self.is_producao:
                self.cell(0, 4, f"Responsável: {self.limpar_texto(self.vendedor)}", ln=1)
            else:
                self.cell(0, 4, f"Vendedor: {self.limpar_texto(self.vendedor)}", ln=1)
            self.cell(100, 4, f"CPF/CNPJ: {self.cliente.get('cnpj', '')}", ln=0)
            self.cell(0, 4, f"Telefone: {self.cliente.get('telefone', '')}", ln=1)
        
        if self.em_tabela:
            self.ln(4)
            self.cabecalho_tabela_estatico()

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(150, 150, 150)
        self.cell(0, 10, f"Pagina {self.page_no()} de {{nb}}", align='C')

    def cabecalho_tabela_estatico(self):
        self.set_fill_color(230, 230, 230)
        self.set_text_color(0, 0, 0)
        self.set_font("Helvetica", "B", 8)
        self.cell(10, 7, "ID", 1, 0, 'C', True)
        if hasattr(self, 'is_producao') and self.is_producao:
            self.cell(145, 7, " DESCRICAO DO ITEM", 1, 0, 'L', True)
            self.cell(35, 7, "QTD", 1, 1, 'C', True)
        else:
            self.cell(100, 7, " DESCRICAO DO ITEM", 1, 0, 'L', True)
            self.cell(15, 7, "QTD", 1, 0, 'C', True)
            self.cell(30, 7, "VALOR UN.", 1, 0, 'C', True)
            self.cell(35, 7, "SUBTOTAL", 1, 1, 'R', True)

    @staticmethod
    def limpar_texto(texto):
        """Remove caracteres especiais que o FPDF não suporta nativamente"""
        if not texto: return ""
        subs = {
            "“": '"', "”": '"', "‘": "'", "’": "'", "—": "-", 
            "–": "-", "•": "-", "…": "...", "ã": "a", "õ": "o",
            "á": "a", "é": "e", "í": "i", "ó": "o", "ú": "u",
            "ç": "c", "Â": "A", "Ê": "E", "Ô": "O"
        }
        for o, s in subs.items(): texto = str(texto).replace(o, s)
        # Converte para Latin-1 ignorando o que não puder converter
        try:
            return texto.encode('latin-1', 'replace').decode('latin-1')
        except:
            return str(texto)

    def calcular_altura_item(self, nome, obs):
        linhas_nome = math.ceil(len(nome) / 60)
        linhas_obs = math.ceil(len(obs) / 75) if obs else 0
        return (linhas_nome * 5) + (linhas_obs * 4) + 6

    @staticmethod
    def criar_pdf(id_orc, empresa, cliente, carrinho, financeiro, vendedor, validade, obs_geral="", prazo_entrega="", fotos=None, estilo="classico"):
        pdf = GeradorPDF(empresa, cliente, id_orc, vendedor, validade, orientation='P', unit='mm', format='A4', estilo=estilo)
        pdf.alias_nb_pages()
        pdf.set_auto_page_break(auto=True, margin=15 if estilo == 'futurista' else 20)
        pdf.add_page()
        
        pdf.em_tabela = True
        pdf.ln(5)
        pdf.cabecalho_tabela_estatico()

        for i, item in enumerate(carrinho):
            nome = GeradorPDF.limpar_texto(item.get('produto', ''))
            obs = GeradorPDF.limpar_texto(item.get('descricao', ''))
            
            altura_prevista = pdf.calcular_altura_item(nome, obs)
            if pdf.get_y() + altura_prevista > 270:
                pdf.add_page()

            y_ini = pdf.get_y()
            pdf.set_xy(20, y_ini)
            pdf.set_font("Helvetica", "B", 8)
            cel_w = 145 if getattr(pdf, 'is_producao', False) else 100
            pdf.multi_cell(cel_w, 5, nome, align='L')
            
            if obs:
                pdf.set_font("Helvetica", "I", 7)
                pdf.set_text_color(100, 100, 100)
                pdf.set_x(20)
                pdf.multi_cell(cel_w, 4, f"Obs: {obs}", align='L')
                pdf.set_text_color(0, 0, 0)

            y_fim = pdf.get_y()
            h_real = max(7, y_fim - y_ini)

            pdf.set_xy(10, y_ini)
            pdf.set_font("Helvetica", "", 8)
            pdf.cell(10, h_real, str(i+1), 1, 0, 'C') 
            if getattr(pdf, 'is_producao', False):
                pdf.cell(145, h_real, "", 1, 0) 
                pdf.cell(35, h_real, str(item.get('qtd', 1)), 1, 1, 'C')
            else:
                pdf.cell(100, h_real, "", 1, 0) 
                pdf.cell(15, h_real, str(item.get('qtd', 1)), 1, 0, 'C')
                pdf.cell(30, h_real, f"R$ {float(item.get('preco_un', 0)):,.2f}", 1, 0, 'C')
                pdf.cell(35, h_real, f"R$ {float(item.get('subtotal', 0)):,.2f}", 1, 1, 'R')

        # --- SEÇÃO FINAL: PAGAMENTO E PRAZOS ---
        pdf.em_tabela = False
        if pdf.get_y() > 220: pdf.add_page()
        
        pdf.ln(5)
        pdf.set_font("Helvetica", "B", 10)
        pdf.cell(155, 10, "VALOR TOTAL: ", 0, 0, 'R')
        pdf.set_fill_color(44, 62, 80); pdf.set_text_color(255, 255, 255)
        pdf.cell(35, 10, f"R$ {financeiro.get('total', 0):,.2f} ", 0, 1, 'R', True)

        pdf.ln(5)
        pdf.set_text_color(44, 62, 80)
        pdf.set_font("Helvetica", "B", 9)
        pdf.cell(0, 6, "OPCOES DE PAGAMENTO E PRAZOS:", ln=1)
        
        pdf.set_font("Helvetica", "", 9)
        pdf.set_text_color(0, 0, 0)
        
        # Lista as opções enviadas (PIX, Cartão, etc)
        opcoes = financeiro.get('opcoes_pagamento', [])
        if opcoes:
            for opt in opcoes:
                pdf.cell(0, 5, f"- {GeradorPDF.limpar_texto(opt)}", ln=1)
        else:
            forma_principal = GeradorPDF.limpar_texto(financeiro.get('forma', 'A Combinar'))
            pdf.cell(0, 5, f"- Forma de Pagamento Principal: {forma_principal}", ln=1)

        prazo_final = GeradorPDF.limpar_texto(financeiro.get('prazo_entrega') or prazo_entrega)
        pdf.cell(0, 5, f"- Prazo de Entrega: {prazo_final}", ln=1)
        
        pdf.cell(0, 5, f"- Validade da Proposta: {validade} dias", ln=1)

        # Notas adicionais se houver (obs_geral técnica)
        if obs_geral:
            pdf.ln(2)
            pdf.set_font("Helvetica", "I", 8)
            pdf.multi_cell(0, 4, f"Observacoes: {GeradorPDF.limpar_texto(obs_geral)}", align='L')

        # --- SEÇÃO DE FOTOS (ANEXO) ---
        if fotos:
            if pdf.get_y() > 200:
                pdf.add_page()
            else:
                pdf.ln(10)
            
            pdf.set_font("Helvetica", "B", 12)
            pdf.cell(0, 10, "ANEXO FOTOGRÁFICO", ln=1, align='C')
            pdf.ln(5)
            
            x_start = 10
            y_start = pdf.get_y()
            largura_foto = 90
            altura_foto = 60
            espaco = 5
            
            for i, foto_item in enumerate(fotos):
                if not foto_item:
                    continue
                
                if i > 0 and i % 8 == 0:
                    pdf.add_page()
                    y_start = 20
                
                col = i % 2
                row_idx = (i // 2) % 4
                
                x = x_start + (col * (largura_foto + espaco))
                y = y_start + (row_idx * (altura_foto + espaco))
                
                try:
                    img_data = base64.b64decode(img_b64)
                    img = Image.open(io.BytesIO(img_data))
                    
                    temp_img_path = f"temp_item_{id_orc}_{i}.png"
                    img.save(temp_img_path)
                    
                    pdf.image(temp_img_path, x, y, largura_foto, altura_foto)
                    if os.path.exists(temp_img_path):
                        os.remove(temp_img_path)
                except Exception as e:
                    print(f"Erro ao processar imagem {i}: {e}")

        # Limpeza segura do arquivo temporário de logo
        output = pdf.output(dest="S")
        if os.path.exists(pdf.temp_logo): os.remove(pdf.temp_logo)

        # RETORNO CRÍTICO EM BYTES
        if isinstance(output, str):
            return output.encode('latin-1', 'replace')
        return output

    @staticmethod
    def criar_guia_producao(id_orc, empresa, cliente, carrinho, obs_geral="", fotos=None, data_obra=None, hora_obra=None, vendedor=""):
        pdf = GeradorPDF(empresa, cliente, id_orc, vendedor, 0, tipo_doc="GUIA DE PRODUÇÃO / INSTALAÇÃO", is_producao=True, data_obra=data_obra, hora_obra=hora_obra, orientation='P', unit='mm', format='A4')
        pdf.alias_nb_pages()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()
        
        pdf.em_tabela = True
        pdf.ln(5)
        pdf.cabecalho_tabela_estatico()

        for i, item in enumerate(carrinho):
            nome = GeradorPDF.limpar_texto(item.get('produto', ''))
            obs = GeradorPDF.limpar_texto(item.get('descricao', ''))
            
            cel_w = 145
            altura_prevista = pdf.calcular_altura_item(nome, obs)
            if pdf.get_y() + altura_prevista > 270:
                pdf.add_page()

            y_ini = pdf.get_y()
            pdf.set_xy(20, y_ini)
            pdf.set_font("Helvetica", "B", 8)
            pdf.multi_cell(cel_w, 5, nome, align='L')
            
            if obs:
                pdf.set_font("Helvetica", "I", 7)
                pdf.set_text_color(100, 100, 100)
                pdf.set_x(20)
                pdf.multi_cell(cel_w, 4, f"Obs: {obs}", align='L')
                pdf.set_text_color(0, 0, 0)

            y_fim = pdf.get_y()
            h_real = max(7, y_fim - y_ini)

            pdf.set_xy(10, y_ini)
            pdf.set_font("Helvetica", "", 8)
            pdf.cell(10, h_real, str(i+1), 1, 0, 'C') 
            pdf.cell(145, h_real, "", 1, 0) 
            pdf.cell(35, h_real, str(item.get('qtd', 1)), 1, 1, 'C')

        pdf.em_tabela = False
        if pdf.get_y() > 200: pdf.add_page()
        
        pdf.ln(5)
        pdf.set_text_color(44, 62, 80)
        pdf.set_font("Helvetica", "B", 10)
        pdf.cell(0, 6, "ASSINATURA E APROVAÇÃO TÉCNICA", ln=1)
        pdf.line(10, pdf.get_y(), 200, pdf.get_y())
        pdf.ln(10)
        
        pdf.cell(90, 6, "___________________________________", align='C')
        pdf.cell(90, 6, "___________________________________", align='C', ln=1)
        
        pdf.set_font("Helvetica", "", 9)
        pdf.cell(90, 6, "Responsável pela Produção", align='C')
        pdf.cell(90, 6, "Recebedor / Conferente", align='C', ln=1)
        
        pdf.ln(5)
        pdf.set_font("Helvetica", "B", 9)
        pdf.cell(0, 6, "OBSERVAÇÕES OPERACIONAIS:", ln=1)
        pdf.set_font("Helvetica", "", 9)
        
        # Linhas em branco para preenchimento manual
        for _ in range(3):
            pdf.cell(0, 6, "." * 130, ln=1)
            
        if obs_geral:
            linhas_filtradas = []
            for linha in str(obs_geral).split('\n'):
                l_upper = linha.upper()
                # Remove linhas que mencionam dinheiro, pagamentos ou condições
                if "R$" in linha or "VALOR" in l_upper or "PAGAMENTO" in l_upper or "CONDIÇÕES" in l_upper or "CONDICOES" in l_upper:
                    continue
                linhas_filtradas.append(linha)
            obs_limpa_total = "\n".join(linhas_filtradas).strip()
            
            if obs_limpa_total:
                pdf.ln(5)
                pdf.set_font("Helvetica", "B", 8)
                pdf.multi_cell(0, 4, f"Observações Importantes: {GeradorPDF.limpar_texto(obs_limpa_total)}", align='L')

        # SEÇÃO DE FOTOS (ANEXO)
        if fotos:
            if pdf.get_y() > 210:
                pdf.add_page()
            else:
                pdf.ln(5)

            pdf.set_font("Helvetica", "B", 12)
            pdf.cell(0, 10, "ANEXO FOTOGRÁFICO DE REFERÊNCIA", ln=1, align='C')
            pdf.ln(5)
            
            x_start = 10
            y_start = pdf.get_y()
            largura_foto = 90
            altura_foto = 60
            espaco = 5
            
            for i, img_b64 in enumerate(fotos):
                if not img_b64: continue
                
                if i > 0 and i % 8 == 0:
                    pdf.add_page()
                    y_start = 20
                
                col = i % 2
                row_idx = (i // 2) % 4
                
                x = x_start + (col * (largura_foto + espaco))
                y = y_start + (row_idx * (altura_foto + espaco))
                
                try:
                    img_data = foto_para_bytes(foto_item)
                    if not img_data:
                        continue
                    img = Image.open(io.BytesIO(img_data))
                    
                    temp_img_path = f"temp_item_prod_{id_orc}_{i}.png"
                    img.save(temp_img_path)
                    
                    pdf.image(temp_img_path, x, y, largura_foto, altura_foto)
                    if os.path.exists(temp_img_path):
                        os.remove(temp_img_path)
                except Exception as e:
                    print(f"Erro ao processar imagem {i}: {e}")

        output = pdf.output(dest="S")
        if getattr(pdf, 'temp_logo', None) and os.path.exists(pdf.temp_logo): 
            try: os.remove(pdf.temp_logo)
            except: pass

        if isinstance(output, str):
            return output.encode('latin-1', 'replace')
        return output

    @staticmethod
    def gerar_html_orcamento(id_orc, empresa, cliente, carrinho, financeiro, vendedor, validade, obs_geral=""):
        """Gera uma versão HTML elegante do orçamento para visualização rápida no navegador"""
        logo_img = ""
        if empresa.get('logo_data'):
            logo_img = f'<img src="data:image/png;base64,{empresa["logo_data"]}" style="max-height: 80px;">'

        itens_html = ""
        for i, item in enumerate(carrinho):
            foto_item = ""
            if item.get('img_data'):
                foto_item = f'<br><img src="data:image/png;base64,{item["img_data"]}" style="max-width: 150px; border-radius: 8px; margin-top: 10px;">'
            
            itens_html += f"""
            <tr>
                <td style="padding: 12px; border-bottom: 1px solid #eee; text-align: center;">{i+1}</td>
                <td style="padding: 12px; border-bottom: 1px solid #eee;">
                    <b>{item.get('produto', '')}</b><br>
                    <small style="color: #666;">{item.get('descricao', '')}</small>
                    {foto_item}
                </td>
                <td style="padding: 12px; border-bottom: 1px solid #eee; text-align: center;">{item.get('qtd', 1)} {item.get('unidade', 'un')}</td>
                <td style="padding: 12px; border-bottom: 1px solid #eee; text-align: right;">R$ {float(item.get('preco_un', 0)):,.2f}</td>
                <td style="padding: 12px; border-bottom: 1px solid #eee; text-align: right; font-weight: bold;">R$ {float(item.get('subtotal', 0)):,.2f}</td>
            </tr>
            """

        condicoes_html = "".join([f"<li>{opt}</li>" for opt in financeiro.get('opcoes_pagamento', [])])

        html = f"""
        <!DOCTYPE html>
        <html lang="pt-br">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Orçamento {id_orc} - {empresa.get('empresa_nome', '')}</title>
            <style>
                body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f4f7f6; color: #333; margin: 0; padding: 20px; }}
                .container {{ max-width: 800px; background: #fff; margin: auto; padding: 40px; border-radius: 15px; box-shadow: 0 10px 25px rgba(0,0,0,0.1); }}
                .header {{ display: flex; justify-content: space-between; align-items: center; border-bottom: 2px solid #eee; padding-bottom: 20px; margin-bottom: 30px; }}
                .empresa-info {{ text-align: right; font-size: 0.9em; color: #666; }}
                .badge {{ background: #2c3e50; color: #fff; padding: 10px 20px; border-radius: 5px; font-weight: bold; margin-bottom: 20px; display: inline-block; }}
                table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
                th {{ background-color: #f8f9fa; padding: 12px; text-align: left; border-bottom: 2px solid #dee2e6; color: #2c3e50; }}
                .total-section {{ margin-top: 30px; text-align: right; }}
                .total-box {{ background: #2c3e50; color: #fff; padding: 15px 30px; display: inline-block; border-radius: 8px; font-size: 1.2em; }}
                .footer {{ margin-top: 40px; font-size: 0.8em; color: #999; text-align: center; border-top: 1px solid #eee; padding-top: 20px; }}
                @media print {{ body {{ background: #fff; padding: 0; }} .container {{ box-shadow: none; border: none; }} }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <div class="logo">{logo_img}</div>
                    <div class="empresa-info">
                        <h2 style="margin:0; color: #2c3e50;">{empresa.get('empresa_nome', '')}</h2>
                        CNPJ: {empresa.get('empresa_cnpj', '')}<br>
                        {empresa.get('empresa_end', '')}, {empresa.get('empresa_num', '')}<br>
                        Tel: {empresa.get('empresa_tel', '')}
                    </div>
                </div>

                <div class="badge">PROPOSTA COMERCIAL #{id_orc}</div>

                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">
                    <div>
                        <h4 style="margin-bottom: 5px; color: #2c3e50;">DESTINATÁRIO</h4>
                        <b>{cliente.get('nome', '')}</b><br>
                        {cliente.get('endereco', '')}, {cliente.get('numero', '')}<br>
                        {cliente.get('cidade', '')} - {cliente.get('estado', '')}<br>
                        CNPJ: {cliente.get('cnpj', '')}
                    </div>
                    <div style="text-align: right;">
                        <h4 style="margin-bottom: 5px; color: #2c3e50;">DETALHES</h4>
                        Data: {datetime.now().strftime('%d/%m/%Y')}<br>
                        Validade: {validade} dias<br>
                        Vendedor: {vendedor}
                    </div>
                </div>

                <table>
                    <thead>
                        <tr>
                            <th>#</th>
                            <th>Descrição</th>
                            <th>Qtd</th>
                            <th style="text-align: right;">Unitário</th>
                            <th style="text-align: right;">Total</th>
                        </tr>
                    </thead>
                    <tbody>
                        {itens_html}
                    </tbody>
                </table>

                <div class="total-section">
                    <div class="total-box">TOTAL: R$ {float(financeiro.get('total', 0)):,.2f}</div>
                </div>

                <div style="margin-top: 30px;">
                    <h4 style="color: #2c3e50; border-bottom: 1px solid #eee; padding-bottom: 5px;">CONDIÇÕES E PRAZOS</h4>
                    <ul>
                        <li><b>Forma:</b> {financeiro.get('forma', '')}</li>
                        <li><b>Prazo de Entrega:</b> {financeiro.get('prazo_entrega', '')}</li>
                        <li><b>Validade da Proposta:</b> {validade} dias</li>
                        {condicoes_html}
                    </ul>
                    {f'<p><b>Observações:</b> {obs_geral}</p>' if obs_geral else ''}
                </div>

                <div class="footer">
                    Este documento é uma proposta comercial válida por {validade} dias.<br>
                    © {datetime.now().year} {empresa.get('empresa_nome', '')}
                </div>
            </div>
        </body>
        </html>
        """
        return html

    @staticmethod
    def upload_pdf(pdf_bytes, nome_arquivo):
        """Faz o upload do arquivo com múltiplas tentativas em diferentes serviços"""
        # Detecta mimetype
        mimetype = "text/html" if nome_arquivo.endswith(".html") else "application/pdf"
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}

        # Lista de serviços para tentar (ordem de prioridade)
        # 1. Catbox.moe (Muito estável)
        try:
            url = "https://catbox.moe/user/api.php"
            data = {"reqtype": "fileupload"}
            files = {"fileToUpload": (nome_arquivo, pdf_bytes, mimetype)}
            response = requests.post(url, data=data, files=files, headers=headers, timeout=20)
            if response.status_code == 200 and response.text.startswith("http"):
                return response.text.strip()
        except: pass

        # 2. Uguu.se (Tentativa com mimetype genérico para evitar 415)
        try:
            url = "https://uguu.se/upload?output=text"
            # Usar octet-stream engana filtros de arquivo que bloqueiam HTML
            files = {"files[]": (nome_arquivo, pdf_bytes, "application/octet-stream")}
            response = requests.post(url, files=files, headers=headers, timeout=20)
            if response.status_code == 200:
                return response.text.strip()
        except: pass

        # 3. 0x0.st (Fallback final)
        try:
            files = {"file": (nome_arquivo, pdf_bytes, "application/octet-stream")}
            response = requests.post("https://0x0.st", files=files, headers=headers, timeout=20)
            if response.status_code == 200:
                return response.text.strip()
        except: pass

        return "ERRO_CONEXAO: Servidores ocupados ou internet restrita"
