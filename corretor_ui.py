"""
Corretor Científico ABNT - Interface Gráfica
Interface moderna com Tkinter para processamento de documentos acadêmicos
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import os
from pathlib import Path
import sys

# Importar módulos do corretor
from corretor import CorretorABNT


class CorretorUI:
    """Interface gráfica para o Corretor ABNT"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Corretor Científico ABNT")
        self.root.geometry("900x700")
        self.root.minsize(800, 600)
        
        # Variáveis
        self.input_file = tk.StringVar()
        self.output_file = tk.StringVar()
        self.verify_links = tk.BooleanVar(value=False)
        self.processing = False
        
        # Configurar estilo
        self._setup_style()
        
        # Criar interface
        self._create_widgets()
        
        # Centralizar janela
        self._center_window()
    
    def _setup_style(self):
        """Configura estilo visual da aplicação"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Cores
        self.colors = {
            'primary': '#2563eb',
            'primary_dark': '#1e40af',
            'success': '#10b981',
            'warning': '#f59e0b',
            'danger': '#ef4444',
            'bg': '#f8fafc',
            'card': '#ffffff',
            'text': '#1e293b',
            'text_secondary': '#64748b',
            'border': '#e2e8f0'
        }
        
        # Configurar estilos
        style.configure('Title.TLabel', 
                       font=('Segoe UI', 18, 'bold'),
                       foreground=self.colors['text'])
        
        style.configure('Subtitle.TLabel',
                       font=('Segoe UI', 10),
                       foreground=self.colors['text_secondary'])
        
        style.configure('Header.TLabel',
                       font=('Segoe UI', 11, 'bold'),
                       foreground=self.colors['text'])
        
        style.configure('Card.TFrame',
                       background=self.colors['card'],
                       relief='flat')
        
        style.configure('Primary.TButton',
                       font=('Segoe UI', 10, 'bold'),
                       padding=(20, 10))
        
        self.root.configure(bg=self.colors['bg'])
    
    def _create_widgets(self):
        """Cria todos os widgets da interface"""
        # Container principal com padding
        main_container = ttk.Frame(self.root, padding="20")
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # Cabeçalho
        self._create_header(main_container)
        
        # Card de entrada
        self._create_input_section(main_container)
        
        # Card de saída
        self._create_output_section(main_container)
        
        # Opções
        self._create_options_section(main_container)
        
        # Botões de ação
        self._create_action_buttons(main_container)
        
        # Área de log
        self._create_log_section(main_container)
        
        # Barra de progresso
        self._create_progress_bar(main_container)
        
        # Rodapé
        self._create_footer(main_container)
    
    def _create_header(self, parent):
        """Cria cabeçalho da aplicação"""
        header_frame = ttk.Frame(parent)
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Ícone e título
        title_frame = ttk.Frame(header_frame)
        title_frame.pack(anchor=tk.W)
        
        icon_label = ttk.Label(title_frame, text="📚", font=('Segoe UI', 24))
        icon_label.pack(side=tk.LEFT, padx=(0, 10))
        
        text_frame = ttk.Frame(title_frame)
        text_frame.pack(side=tk.LEFT)
        
        title = ttk.Label(text_frame, text="Corretor Científico ABNT", style='Title.TLabel')
        title.pack(anchor=tk.W)
        
        subtitle = ttk.Label(text_frame, 
                           text="Processador profissional de documentos acadêmicos",
                           style='Subtitle.TLabel')
        subtitle.pack(anchor=tk.W)
    
    def _create_input_section(self, parent):
        """Cria seção de seleção de arquivo de entrada"""
        # Card container
        card = self._create_card(parent, "📄 Documento de Entrada")
        
        # Frame interno
        input_frame = ttk.Frame(card)
        input_frame.pack(fill=tk.X, padx=15, pady=(0, 15))
        
        # Label
        label = ttk.Label(input_frame, text="Selecione o arquivo Word (.docx) ou PDF:")
        label.pack(anchor=tk.W, pady=(0, 8))
        
        # Entry e botão
        entry_frame = ttk.Frame(input_frame)
        entry_frame.pack(fill=tk.X)
        
        entry = ttk.Entry(entry_frame, textvariable=self.input_file, font=('Segoe UI', 10))
        entry.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        btn = ttk.Button(entry_frame, text="Procurar...", command=self._browse_input)
        btn.pack(side=tk.RIGHT)
    
    def _create_output_section(self, parent):
        """Cria seção de seleção de arquivo de saída"""
        card = self._create_card(parent, "💾 Arquivo de Saída")
        
        output_frame = ttk.Frame(card)
        output_frame.pack(fill=tk.X, padx=15, pady=(0, 15))
        
        label = ttk.Label(output_frame, text="Local para salvar o documento Word processado:")
        label.pack(anchor=tk.W, pady=(0, 8))
        
        entry_frame = ttk.Frame(output_frame)
        entry_frame.pack(fill=tk.X)
        
        entry = ttk.Entry(entry_frame, textvariable=self.output_file, font=('Segoe UI', 10))
        entry.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        btn = ttk.Button(entry_frame, text="Procurar...", command=self._browse_output)
        btn.pack(side=tk.RIGHT)
    
    def _create_options_section(self, parent):
        """Cria seção de opções"""
        card = self._create_card(parent, "⚙️ Opções")
        
        options_frame = ttk.Frame(card)
        options_frame.pack(fill=tk.X, padx=15, pady=(0, 15))
        
        # Checkbox para verificar links
        check = ttk.Checkbutton(options_frame,
                               text="Verificar URLs e atualizar datas de acesso (mais lento)",
                               variable=self.verify_links)
        check.pack(anchor=tk.W, pady=5)
        
        # Info adicional
        info = ttk.Label(options_frame,
                        text="• Converte citações numéricas para formato autor-data\n"
                             "• Formata referências conforme ABNT NBR 6023\n"
                             "• Preserva formatação do documento original",
                        foreground=self.colors['text_secondary'],
                        font=('Segoe UI', 9))
        info.pack(anchor=tk.W, pady=(10, 0))
    
    def _create_action_buttons(self, parent):
        """Cria botões de ação"""
        btn_frame = ttk.Frame(parent)
        btn_frame.pack(fill=tk.X, pady=20)
        
        # Botão processar
        self.process_btn = tk.Button(btn_frame,
                                     text="🚀 Processar Documento",
                                     command=self._process_document,
                                     bg=self.colors['primary'],
                                     fg='white',
                                     font=('Segoe UI', 11, 'bold'),
                                     relief=tk.FLAT,
                                     cursor='hand2',
                                     padx=30,
                                     pady=12)
        self.process_btn.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 10))
        
        # Efeito hover
        self.process_btn.bind('<Enter>', lambda e: self.process_btn.config(bg=self.colors['primary_dark']))
        self.process_btn.bind('<Leave>', lambda e: self.process_btn.config(bg=self.colors['primary']))
        
        # Botão limpar
        clear_btn = tk.Button(btn_frame,
                             text="🗑️ Limpar",
                             command=self._clear_fields,
                             bg=self.colors['text_secondary'],
                             fg='white',
                             font=('Segoe UI', 11),
                             relief=tk.FLAT,
                             cursor='hand2',
                             padx=20,
                             pady=12)
        clear_btn.pack(side=tk.RIGHT)
    
    def _create_log_section(self, parent):
        """Cria área de log"""
        card = self._create_card(parent, "📋 Log de Processamento")
        
        log_frame = ttk.Frame(card)
        log_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 15))
        
        # Text widget com scrollbar
        self.log_text = scrolledtext.ScrolledText(log_frame,
                                                  height=10,
                                                  font=('Consolas', 9),
                                                  bg='#1e293b',
                                                  fg='#e2e8f0',
                                                  relief=tk.FLAT,
                                                  padx=10,
                                                  pady=10)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        self.log_text.config(state=tk.DISABLED)
    
    def _create_progress_bar(self, parent):
        """Cria barra de progresso"""
        self.progress = ttk.Progressbar(parent, mode='indeterminate', length=300)
        self.progress.pack(fill=tk.X, pady=(0, 10))
    
    def _create_footer(self, parent):
        """Cria rodapé"""
        footer = ttk.Label(parent,
                          text="Desenvolvido com Python • ABNT NBR 6023 & NBR 10520",
                          font=('Segoe UI', 8),
                          foreground=self.colors['text_secondary'])
        footer.pack(pady=(10, 0))
    
    def _create_card(self, parent, title):
        """Cria um card com título"""
        # Container externo
        container = ttk.Frame(parent)
        container.pack(fill=tk.X, pady=(0, 15))
        
        # Card
        card = tk.Frame(container,
                       bg=self.colors['card'],
                       relief=tk.FLAT,
                       highlightbackground=self.colors['border'],
                       highlightthickness=1)
        card.pack(fill=tk.X)
        
        # Título do card
        title_label = ttk.Label(card, text=title, style='Header.TLabel')
        title_label.pack(anchor=tk.W, padx=15, pady=(15, 10))
        
        return card
    
    def _center_window(self):
        """Centraliza a janela na tela"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def _browse_input(self):
        """Abre diálogo para selecionar arquivo de entrada"""
        filename = filedialog.askopenfilename(
            title="Selecione o documento",
            filetypes=[
                ("Documentos Word", "*.docx"),
                ("Documentos PDF", "*.pdf"),
                ("Todos os arquivos", "*.*")
            ]
        )
        
        if filename:
            self.input_file.set(filename)
            
            # Auto-preencher saída
            if not self.output_file.get():
                path = Path(filename)
                output = path.parent / f"{path.stem}(REV-ABNT).docx"
                self.output_file.set(str(output))
    
    def _browse_output(self):
        """Abre diálogo para selecionar arquivo de saída"""
        filename = filedialog.asksaveasfilename(
            title="Salvar como",
            defaultextension=".docx",
            filetypes=[
                ("Documento Word", "*.docx"),
                ("Todos os arquivos", "*.*")
            ]
        )
        
        if filename:
            self.output_file.set(filename)
    
    def _clear_fields(self):
        """Limpa todos os campos"""
        self.input_file.set("")
        self.output_file.set("")
        self.verify_links.set(False)
        self._clear_log()
    
    def _clear_log(self):
        """Limpa o log"""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state=tk.DISABLED)
    
    def _log(self, message, level="info"):
        """Adiciona mensagem ao log"""
        self.log_text.config(state=tk.NORMAL)
        
        # Cores por nível
        colors = {
            'info': '#60a5fa',
            'success': '#34d399',
            'warning': '#fbbf24',
            'error': '#f87171'
        }
        
        # Ícones por nível
        icons = {
            'info': 'ℹ️',
            'success': '✅',
            'warning': '⚠️',
            'error': '❌'
        }
        
        icon = icons.get(level, 'ℹ️')
        timestamp = Path(__file__).stat().st_mtime  # Placeholder
        
        self.log_text.insert(tk.END, f"{icon} {message}\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)
        self.root.update()
    
    def _validate_inputs(self):
        """Valida os campos de entrada"""
        if not self.input_file.get():
            messagebox.showerror("Erro", "Selecione um arquivo de entrada!")
            return False
        
        if not os.path.exists(self.input_file.get()):
            messagebox.showerror("Erro", "Arquivo de entrada não encontrado!")
            return False
        
        if not self.output_file.get():
            messagebox.showerror("Erro", "Especifique o arquivo de saída!")
            return False
        
        # Verificar extensão
        ext = Path(self.input_file.get()).suffix.lower()
        if ext not in ['.docx', '.pdf']:
            messagebox.showerror("Erro", "Formato não suportado! Use .docx ou .pdf")
            return False
        
        return True
    
    def _process_document(self):
        """Processa o documento em thread separada"""
        if self.processing:
            messagebox.showwarning("Aviso", "Processamento em andamento...")
            return
        
        if not self._validate_inputs():
            return
        
        # Iniciar processamento
        self.processing = True
        self.process_btn.config(state=tk.DISABLED, text="Processando...")
        self.progress.start(10)
        self._clear_log()
        
        # Executar em thread separada
        thread = threading.Thread(target=self._run_processing, daemon=True)
        thread.start()
    
    def _run_processing(self):
        """Executa o processamento do documento"""
        try:
            self._log("Iniciando processamento...", "info")
            
            # Criar corretor
            corretor = CorretorABNT(
                input_file=self.input_file.get(),
                output_file=self.output_file.get(),
                verify_links=self.verify_links.get()
            )
            
            # Processar com callbacks de log
            self._log("📖 Extraindo conteúdo do documento...", "info")
            corretor.extract_document()
            self._log("✓ Conteúdo extraído com sucesso", "success")
            
            self._log("📚 Extraindo referências bibliográficas...", "info")
            corretor.extract_references()
            self._log(f"✓ {len(corretor.references)} referências encontradas", "success")
            
            self._log("🔄 Processando citações...", "info")
            corretor.process_citations()
            self._log("✓ Citações processadas", "success")
            
            self._log("📋 Formatando referências ABNT...", "info")
            corretor.format_references()
            self._log("✓ Referências formatadas", "success")
            
            if self.verify_links.get():
                self._log("🔗 Verificando links (pode demorar)...", "warning")
                corretor.verify_and_update_links()
                self._log("✓ Links verificados", "success")
            
            self._log("🔍 Validando documento corrigido...", "info")
            corretor.validate_document_after()
            self._log("✓ Validação concluída", "success")
            
            self._log("💾 Exportando para Word (DOCX)...", "info")
            corretor.export_docx()
            self._log("✓ Documento Word exportado", "success")
            
            self._log("📝 Gerando relatório de alterações...", "info")
            corretor.generate_final_report()
            self._log("✓ Relatório gerado", "success")
            
            # Sucesso
            self._log("", "info")
            self._log("🎉 PROCESSAMENTO CONCLUÍDO COM SUCESSO!", "success")
            self._log(f"📄 Arquivo salvo: {self.output_file.get()}", "info")
            
            # Mostrar diálogo de sucesso
            self.root.after(100, lambda: self._show_success_dialog())
            
        except Exception as e:
            self._log(f"Erro durante processamento: {str(e)}", "error")
            self.root.after(100, lambda: messagebox.showerror("Erro", f"Erro ao processar documento:\n{str(e)}"))
        
        finally:
            # Restaurar interface
            self.root.after(100, self._finish_processing)
    
    def _finish_processing(self):
        """Finaliza o processamento e restaura a interface"""
        self.processing = False
        self.process_btn.config(state=tk.NORMAL, text="🚀 Processar Documento")
        self.progress.stop()
    
    def _show_success_dialog(self):
        """Mostra diálogo de sucesso com opções"""
        # Calcular caminho do relatório
        output_path = Path(self.output_file.get())
        report_path = output_path.parent / f"{output_path.stem}_RELATORIO.md"
        
        # Mensagem com informações sobre os arquivos gerados
        message = (
            "Documento processado com sucesso!\n\n"
            f"📄 Documento corrigido: {output_path.name}\n"
            f"📝 Relatório de alterações: {report_path.name}\n\n"
            "Deseja abrir o documento gerado?"
        )
        
        result = messagebox.askyesno(
            "Sucesso!",
            message,
            icon=messagebox.QUESTION
        )
        
        if result:
            try:
                os.startfile(self.output_file.get())
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao abrir arquivo:\n{str(e)}")


def main():
    """Função principal"""
    root = tk.Tk()
    app = CorretorUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
