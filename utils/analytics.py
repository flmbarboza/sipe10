import streamlit as st
import time
import json
from datetime import datetime
import pandas as pd

class UXMonitor:
    def __init__(self):
        if 'analytics' not in st.session_state:
            st.session_state.analytics = {
                'events': [],          # Todos os eventos brutos
                'sessions': [],        # Resumo por sessão
                'page_timers': {}      # Para medir tempo por página
            }
    
    def track_event(self, event_type, page, metadata=None):
        """Registra um evento do usuário"""
        event = {
            'timestamp': datetime.now().isoformat(),
            'session_id': st.session_state.get('session_id', 'unknown'),
            'event_type': event_type,  # page_view, click, export, ai_call, error
            'page': page,
            'metadata': metadata or {},
            'user_agent': st.query_params.get('ua', 'unknown')
        }
        st.session_state.analytics['events'].append(event)
        
        # Se for evento de página, marca o início do timer
        if event_type == 'page_view':
            st.session_state.analytics['page_timers'][page] = time.time()
    
    def track_page_time(self, page):
        """Calcula o tempo gasto em uma página quando o usuário sai dela"""
        if page in st.session_state.analytics['page_timers']:
            start_time = st.session_state.analytics['page_timers'].pop(page)
            duration = time.time() - start_time
            self.track_event('page_duration', page, {'seconds': round(duration, 2)})
    
    def track_error(self, page, error_type, error_msg):
        """Registra erros para identificar pontos de fricção"""
        self.track_event('error', page, {
            'error_type': error_type,
            'message': str(error_msg)[:200]  # Limita para não poluir
        })
    
    def get_insights(self):
        """Gera insights agregados para o desenvolvedor"""
        df = pd.DataFrame(st.session_state.analytics['events'])
        if df.empty:
            return "Ainda não há dados suficientes."
        
        insights = []
        
        # 1. Páginas mais acessadas
        page_views = df[df.event_type == 'page_view'].page.value_counts()
        insights.append(f"📊 Páginas mais acessadas:\n{page_views.head(3).to_string()}")
        
        # 2. Tempo médio por página (em segundos)
        durations = df[df.event_type == 'page_duration']
        if not durations.empty:
            avg_time = durations['metadata'].apply(lambda x: x.get('seconds', 0)).mean()
            insights.append(f"⏱️ Tempo médio por página: {avg_time:.1f}s")
        
        # 3. Taxa de uso da IA
        ai_calls = len(df[df.event_type == 'ai_call'])
        total_sessions = df.session_id.nunique()
        insights.append(f"🤖 Chamadas à IA por sessão: {ai_calls/total_sessions if total_sessions>0 else 0:.1f}")
        
        # 4. Taxa de erro
        errors = len(df[df.event_type == 'error'])
        insights.append(f"❌ Taxa de erro: {(errors/len(df)*100) if len(df)>0 else 0:.1f}%")
        
        # 5. Funil de conversão (sequência esperada vs. real)
        expected_flow = ['Business Model Canvas', 'PESTEL', '5 Forças', 'SWOT', 
                         'Planejamento Estratégico', 'Plano Financeiro', 'Plano de Ação']
        actual_flow = df[df.event_type == 'page_view'].page.tolist()
        # Análise de desvio do fluxo esperado
        deviations = self._analyze_flow(actual_flow, expected_flow)
        insights.append(f"🔗 Desvio do fluxo ideal: {deviations}%")
        
        return "\n\n".join(insights)
    
    def _analyze_flow(self, actual, expected):
        """Calcula o % de desvio da ordem esperada"""
        if not actual or not expected:
            return 100
        # Implementação simplificada de distância de Levenshtein para sequências
        matches = sum(1 for a, e in zip(actual, expected) if a == e)
        return round((1 - matches/len(expected)) * 100)
