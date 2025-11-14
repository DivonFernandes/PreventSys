<script>
    // Leitor de Tela Flutuante - CORRIGIDO (Modo seleção sem alterar estilos)
    class LeitorFlutuante {
        constructor() {
            this.ativo = false;
            this.synth = window.speechSynthesis;
            this.utterance = null;
            this.velocidade = 1.0;
            this.volume = 1.0;
            this.vozPortugues = null;
            this.modoSelecaoAtivo = false;
            this.elementosSelecao = [];
            
            this.inicializarVoz();
            this.adicionarListeners();
            this.verificarEstadoSalvo();
        }

        // ... (mantenha os métodos existentes até o método ativarModoSelecao)

        ativarModoSelecao() {
            if (!this.ativo) return;

            this.modoSelecaoAtivo = true;
            this.falar('Modo de seleção ativado. Clique em qualquer elemento da página para ouvir seu conteúdo. Pressione Escape para sair.');

            // Selecionar elementos sem modificar seus estilos originais
            this.elementosSelecao = Array.from(document.querySelectorAll(
                'h1, h2, h3, h4, h5, h6, p, a, button, label, li, td, th, input, select, textarea, .card, .btn, .form-control'
            ));

            // Aplicar overlay sutil sem alterar estilos dos elementos
            this.elementosSelecao.forEach(elemento => {
                const rect = elemento.getBoundingClientRect();
                if (rect.width > 0 && rect.height > 0) { // Elementos visíveis apenas
                    // Criar overlay sutil
                    const overlay = document.createElement('div');
                    overlay.className = 'leitor-overlay';
                    overlay.style.cssText = `
                        position: absolute;
                        left: ${rect.left + window.scrollX}px;
                        top: ${rect.top + window.scrollY}px;
                        width: ${rect.width}px;
                        height: ${rect.height}px;
                        background-color: rgba(85, 107, 47, 0.1);
                        border: 2px dashed #556B2F;
                        border-radius: 4px;
                        cursor: pointer;
                        z-index: 9998;
                        pointer-events: auto;
                        transition: all 0.2s ease;
                    `;
                    
                    // Armazenar referência ao elemento original
                    overlay.dataset.elementId = this.elementosSelecao.indexOf(elemento);
                    
                    overlay.addEventListener('click', (e) => {
                        e.preventDefault();
                        e.stopPropagation();
                        this.lerElementoViaOverlay(elemento);
                    });
                    
                    overlay.addEventListener('mouseenter', () => {
                        overlay.style.backgroundColor = 'rgba(85, 107, 47, 0.2)';
                        overlay.style.border = '2px solid #556B2F';
                    });
                    
                    overlay.addEventListener('mouseleave', () => {
                        overlay.style.backgroundColor = 'rgba(85, 107, 47, 0.1)';
                        overlay.style.border = '2px dashed #556B2F';
                    });
                    
                    document.body.appendChild(overlay);
                    elemento.leitorOverlay = overlay;
                }
            });

            document.getElementById('leitor-status-global').textContent = 'Modo seleção ATIVO - clique nos elementos';
            document.getElementById('btn-ler-elemento-global').textContent = '🔴 Sair do Modo Seleção';
        }

        lerElementoViaOverlay(elemento) {
            if (!this.modoSelecaoAtivo) return;

            const texto = this.extrairTextoElemento(elemento);

            if (texto) {
                // Destacar temporariamente com overlay
                if (elemento.leitorOverlay) {
                    elemento.leitorOverlay.style.backgroundColor = 'rgba(255, 193, 7, 0.3)';
                    elemento.leitorOverlay.style.border = '2px solid #FFC107';
                    
                    setTimeout(() => {
                        if (elemento.leitorOverlay) {
                            elemento.leitorOverlay.style.backgroundColor = 'rgba(85, 107, 47, 0.1)';
                            elemento.leitorOverlay.style.border = '2px dashed #556B2F';
                        }
                    }, 2000);
                }
                
                this.falar(texto, 'alta');
            }
        }

        desativarModoSelecao() {
            if (!this.modoSelecaoAtivo) return;

            this.modoSelecaoAtivo = false;
            
            // Remover todos os overlays
            this.elementosSelecao.forEach(elemento => {
                if (elemento.leitorOverlay) {
                    elemento.leitorOverlay.remove();
                    elemento.leitorOverlay = null;
                }
            });
            
            this.elementosSelecao = [];

            document.getElementById('leitor-status-global').textContent = 'Modo seleção desativado';
            document.getElementById('btn-ler-elemento-global').textContent = '🔍 Ler Elemento';
        }

        // Modifique o método toggleModoSelecao
        toggleModoSelecao() {
            if (this.modoSelecaoAtivo) {
                this.desativarModoSelecao();
            } else {
                this.ativarModoSelecao();
            }
        }

        // Atualize o método fecharPainel para desativar modo seleção
        fecharPainel() {
            const painel = document.getElementById('painel-leitor-global');
            if (painel) {
                painel.classList.remove('mostrar');
            }
            this.desativarModoSelecao();
        }

        // ... (mantenha os demais métodos existentes)
    }

    // Inicializar leitor quando o DOM estiver carregado
    document.addEventListener('DOMContentLoaded', () => {
        window.leitorFlutuante = new LeitorFlutuante();
        
        // Anúncio inicial se estiver ativo
        setTimeout(() => {
            if (window.leitorFlutuante && window.leitorFlutuante.ativo) {
                const paginaAtual = document.title || 'Página atual';
                window.leitorFlutuante.falar(`${paginaAtual} carregada. Leitor de tela ativo.`);
            }
        }, 1000);
    });
</script>