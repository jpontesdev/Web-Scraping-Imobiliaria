import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import statsmodels.api as sm
from statsmodels.stats.outliers_influence import variance_inflation_factor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression, Ridge, Lasso
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error

class LinearRegressionService():
    def __init__(self, file_path='data_propriety copy.csv'):
        self.file_path = file_path
        self.df = None
        self.df_filtered = None
        self.X = None
        self.y = None
        self.X_train = None
        self.X_test = None
        self.y_train = None
        self.y_test = None
        self.scaler = None
        self.X_train_scaled = None
        self.X_test_scaled = None
        self.models = {}
        self.predictions = {}

    def clean_data(self):
        """Etapa 2: Carregamento, Limpeza, Tratamento de Outliers (IQR) e Variável Derivada"""
        print("--- 1. Carregando e Limpando os Dados ---")
        self.df = pd.read_csv(self.file_path)

        if 'id' in self.df.columns:
            self.df.drop(columns=['id'], inplace=True)

        self.df.dropna(inplace=True)

        # Criar variável price_m2
        self.df['price_m2'] = self.df['Price'] / self.df['m2']

        # Remover Outliers pelo critério de 3x IQR no Preço
        q1 = self.df['Price'].quantile(0.25)
        q3 = self.df['Price'].quantile(0.75)
        iqr = q3 - q1
        limite_superior = q3 + 3 * iqr

        self.df_filtered = self.df[self.df['Price'] <= limite_superior].copy()

        print(f"Dataset original: {len(self.df)} registros.")
        print(f"Dataset pós-remoção de outliers (> R$ {limite_superior:.2f}): {len(self.df_filtered)} registros.\n")

    def run_eda(self):
        """Etapa 3: Análise Exploratória de Dados (EDA)"""
        print("--- 2. Executando Análise Exploratória (EDA) ---")
        
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))

        # 1. Histogramas de Price e price_m2
        sns.histplot(self.df_filtered['Price'], kde=True, ax=axes[0, 0], color='blue')
        axes[0, 0].set_title('Distribuição do Preço (R$)')
        axes[0, 0].set_xlabel('Preço (R$)')

        sns.histplot(self.df_filtered['price_m2'], kde=True, ax=axes[0, 1], color='green')
        axes[0, 1].set_title('Distribuição do Preço por m² (R$/m²)')
        axes[0, 1].set_xlabel('Preço/m² (R$)')

        # 2. Matriz de Correlação
        num_cols = ['Price', 'm2', 'quartos', 'banheiros', 'vagas', 'price_m2']
        sns.heatmap(self.df_filtered[num_cols].corr(), annot=True, cmap='Blues', fmt=".2f", ax=axes[1, 0])
        axes[1, 0].set_title('Matriz de Correlação')

        # 3. Scatter Plot m2 x Price com Reta de Tendência
        sns.regplot(data=self.df_filtered, x='m2', y='Price', ax=axes[1, 1],
                    scatter_kws={'alpha': 0.6}, line_kws={'color': 'red'})
        axes[1, 1].set_title('Área (m²) vs Preço (R$)')
        axes[1, 1].set_xlabel('Área (m²)')
        axes[1, 1].set_ylabel('Preço (R$)')

        plt.tight_layout()
        plt.show(block=False)
        plt.pause(1)

        # 4. Boxplot dos Top 10 Bairros
        top_10_bairros = self.df_filtered['neighborhood'].value_counts().head(10).index
        df_top10 = self.df_filtered[self.df_filtered['neighborhood'].isin(top_10_bairros)]

        plt.figure(figsize=(12, 6))
        sns.boxplot(
            data=df_top10, 
            x='neighborhood', 
            y='Price', 
            hue='neighborhood', 
            palette='Set3', 
            legend=False
        )
        plt.title('Distribuição de Preço nos Top 10 Bairros com Mais Anúncios')
        plt.xlabel('Bairro')
        plt.ylabel('Preço (R$)')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show(block=False)
        plt.pause(1)

    def run_statistical_analysis(self):
        """Estatística OLS via Statsmodels"""
        print("\n--- 3. Análise Estatística OLS (Statsmodels) ---")
        X_baseline = self.df_filtered[['m2', 'quartos', 'banheiros', 'vagas']]
        y_baseline = self.df_filtered['Price']

        X_baseline_const = sm.add_constant(X_baseline)
        ols_model = sm.OLS(y_baseline, X_baseline_const).fit()
        print(ols_model.summary())

    def transform_features(self):
        """Etapa 4: Engenharia de Recursos, Log e One-Hot Encoding"""
        print("\n--- 4. Tratamento e Transformação de Features ---")
        df_proc = self.df_filtered.copy()

        # Agrupar bairros com poucas observações para evitar alta dimensionalidade
        top_neighborhoods = df_proc['neighborhood'].value_counts()
        top_neighborhoods = top_neighborhoods[top_neighborhoods >= 5].index
        df_proc['neighborhood'] = df_proc['neighborhood'].apply(
            lambda x: x if x in top_neighborhoods else 'Outros'
        )

        # Transformação logarítmica no Preço
        df_proc['Price_log'] = np.log1p(df_proc['Price'])

        # One-Hot Encoding dos Bairros
        df_proc = pd.get_dummies(df_proc, columns=['neighborhood'], drop_first=True, dtype=float)

        # Separar Preditores e Alvo
        self.X = df_proc.drop(columns=['Price', 'Price_log', 'price_m2'])
        self.y = df_proc['Price_log']

    def calculate_vif(self):
        """Diagnóstico de Multicolinearidade (VIF)"""
        print("\n--- 5. Cálculo do VIF (Multicolinearidade) ---")
        X_num = self.df_filtered[['m2', 'quartos', 'banheiros', 'vagas']]
        vif_data = pd.DataFrame()
        vif_data["Feature"] = X_num.columns
        vif_data["VIF"] = [variance_inflation_factor(X_num.values, i) for i in range(X_num.shape[1])]
        print(vif_data)

    def split_data(self):
        """Divisão Treino / Teste"""
        print("\n--- 6. Divisão Treino / Teste ---")
        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(
            self.X, self.y, test_size=0.20, random_state=42
        )
        print(f"Treino: {self.X_train.shape[0]} amostras | Teste: {self.X_test.shape[0]} amostras")

    def train_and_compare(self):
        """Etapa 4: Treinamento e Comparação com Ridge e Lasso"""
        print("\n--- 7. Treinamento e Comparação de Modelos ---")
        self.scaler = StandardScaler()

        self.X_train_scaled = self.scaler.fit_transform(self.X_train)
        self.X_test_scaled = self.scaler.transform(self.X_test)

        self.models = {
            'Regressão Linear Múltipla': LinearRegression(),
            'Regressão Ridge (L2)': Ridge(alpha=1.0),
            'Regressão Lasso (L1)': Lasso(alpha=0.01)
        }

        print(f"{'Modelo':<30} | {'R² Treino':<10} | {'R² Teste':<10} | {'MAE (R$)':<10} | {'RMSE (R$)':<10}")
        print("-" * 80)

        for name, model in self.models.items():
            model.fit(self.X_train_scaled, self.y_train)
            
            y_pred_train_log = model.predict(self.X_train_scaled)
            y_pred_test_log = model.predict(self.X_test_scaled)
            
            self.predictions[name] = y_pred_test_log

            r2_tr = r2_score(self.y_train, y_pred_train_log)
            r2_te = r2_score(self.y_test, y_pred_test_log)

            # Reverter log
            y_test_real = np.expm1(self.y_test)
            y_pred_real = np.expm1(y_pred_test_log)

            mae = mean_absolute_error(y_test_real, y_pred_real)
            rmse = np.sqrt(mean_squared_error(y_test_real, y_pred_real))

            print(f"{name:<30} | {r2_tr:<10.4f} | {r2_te:<10.4f} | {mae:<10.2f} | {rmse:<10.2f}")

    def interpret_coefficients(self):
        """Etapa 5: Interpretação dos Coeficientes"""
        print("\n--- 8. Interpretação dos Coeficientes (Regressão Múltipla) ---")
        lr = self.models['Regressão Linear Múltipla']
        
        coef_df = pd.DataFrame({
            'Feature': self.X.columns,
            'Coeficiente_Padronizado': lr.coef_
        }).sort_values(by='Coeficiente_Padronizado', ascending=False)

        print(coef_df.to_string(index=False))

    def plot_results(self):
        """Gráficos de Desempenho"""
        y_test_real = np.expm1(self.y_test)
        y_pred_real = np.expm1(self.predictions['Regressão Linear Múltipla'])

        plt.figure(figsize=(8, 5))
        plt.scatter(y_test_real, y_pred_real, alpha=0.7, color='blue')
        plt.plot([y_test_real.min(), y_test_real.max()], [y_test_real.min(), y_test_real.max()], 'r--', lw=2)
        plt.xlabel('Preço Real (R$)')
        plt.ylabel('Preço Previsto (R$)')
        plt.title('Preços Reais vs. Preços Previstos (Base de Teste - Sem Outliers)')
        plt.grid(True)
        plt.tight_layout()
        plt.show(block=False)
        plt.pause(1)

        plt.show()