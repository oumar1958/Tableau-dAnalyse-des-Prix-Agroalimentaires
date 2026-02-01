def advanced_features_page():
    """Page avec fonctionnalités avancées de niveau expert"""
    st.header("🚀 Features Avancées - Niveau Expert")
    
    df = load_data()
    if df is None:
        st.error("Impossible de charger les données")
        return
    
    advanced = AdvancedFeatures(df)
    
    # Navigation par onglets
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "🧠 Sentiment Market", "🔍 Anomalies", "🎯 Clustering", 
        "📊 Elasticite", "📡 Monitoring Live", "💼 Portfolio Optimizer"
    ])
    
    with tab1:
        st.subheader("🧠 Analyseur de Sentiment du Marche")
        
        sentiment_data = advanced.create_market_sentiment_analyzer()
        
        # Metriques globales
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            positive_sentiment = len(sentiment_data[sentiment_data['sentiment_score'] >= 70])
            st.metric("🟢 Sentiment Positif", positive_sentiment)
        
        with col2:
            neutral_sentiment = len(sentiment_data[(sentiment_data['sentiment_score'] >= 40) & (sentiment_data['sentiment_score'] < 70)])
            st.metric("🟡 Sentiment Neutre", neutral_sentiment)
        
        with col3:
            negative_sentiment = len(sentiment_data[sentiment_data['sentiment_score'] < 40])
            st.metric("🔴 Sentiment Negatif", negative_sentiment)
        
        with col4:
            avg_sentiment = sentiment_data['sentiment_score'].mean()
            st.metric("📊 Sentiment Moyen", f"{avg_sentiment:.1f}/100")
        
        # Visualisation du sentiment
        fig = px.scatter(
            sentiment_data,
            x='volatility',
            y='trend',
            color='sentiment_score',
            size='stability',
            hover_name='product',
            title='Carte de Sentiment du Marche',
            color_continuous_scale='RdYlGn'
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Tableau detaille
        st.subheader("📋 Analyse de Sentiment par Produit")
        sentiment_display = sentiment_data.sort_values('sentiment_score', ascending=False)
        st.dataframe(sentiment_display.round(2), use_container_width=True)
    
    with tab2:
        st.subheader("🔍 Detecteur d'Anomalies de Prix")
        
        anomalies = advanced.create_price_anomaly_detector()
        
        if not anomalies.empty:
            st.warning(f"🚨 {len(anomalies)} anomalie(s) detectee(s)")
            
            # Visualisation des anomalies
            fig = go.Figure()
            
            for product in anomalies['product'].unique()[:10]:  # Top 10
                product_data = df[df['product_clean'] == product].sort_values('date')
                product_anomalies = anomalies[anomalies['product'] == product]
                
                # Prix normaux
                fig.add_trace(go.Scatter(
                    x=product_data['date'],
                    y=product_data['price'],
                    mode='lines',
                    name=f'{product} (normal)',
                    line=dict(width=1)
                ))
                
                # Anomalies
                if not product_anomalies.empty:
                    fig.add_trace(go.Scatter(
                        x=product_anomalies['date'],
                        y=product_anomalies['price'],
                        mode='markers',
                        name=f'{product} (anomalie)',
                        marker=dict(size=10, symbol='x', color='red')
                    ))
            
            fig.update_layout(
                title='Detection d\'Anomalies de Prix',
                xaxis_title='Date',
                yaxis_title='Prix (€)',
                height=500
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Tableau des anomalies
            st.subheader("📋 Detail des Anomalies")
            st.dataframe(anomalies.round(2), use_container_width=True)
        else:
            st.success("✅ Aucune anomalie detectee")
    
    with tab3:
        st.subheader("🎯 Clustering Intelligent des Marches")
        
        market_clusters, kmeans, X_scaled = advanced.create_market_clustering()
        
        # Visualisation 3D des clusters
        fig = px.scatter_3d(
            market_clusters,
            x='avg_price',
            y='price_volatility',
            z='product_diversity',
            color='cluster_name',
            hover_name='market',
            size='observation_frequency',
            title='Clustering 3D des Marches'
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Analyse des clusters
        st.subheader("📊 Analyse des Clusters")
        
        for cluster_name in market_clusters['cluster_name'].unique():
            cluster_data = market_clusters[market_clusters['cluster_name'] == cluster_name]
            
            with st.expander(f"📁 {cluster_name} ({len(cluster_data)} marches)"):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Prix moyen", f"{cluster_data['avg_price'].mean():.2f}€")
                
                with col2:
                    st.metric("Volatilite", f"{cluster_data['price_volatility'].mean():.3f}")
                
                with col3:
                    st.metric("Diversite", f"{cluster_data['product_diversity'].mean():.1f}")
                
                st.dataframe(cluster_data[['market', 'avg_price', 'price_volatility', 'product_diversity']].round(2))
    
    with tab4:
        st.subheader("📊 Analyse d'Elasticite des Prix")
        
        elasticity_data = advanced.create_price_elasticity_analyzer()
        
        # Distribution de l'elasticite
        fig = px.histogram(
            elasticity_data,
            x='elasticity',
            color='elasticity_category',
            title='Distribution de l\'Elasticite des Prix',
            nbins=20
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Matrice de sensibilite
        st.subheader("🎯 Matrice de Sensibilite")
        
        elasticity_pivot = elasticity_data.pivot_table(
            index='product',
            columns='elasticity_category',
            values='elasticity',
            fill_value=0
        )
        
        fig = px.imshow(
            elasticity_pivot,
            title='Matrice d\'Elasticite par Produit',
            color_continuous_scale='Viridis'
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Tableau detaille
        st.dataframe(elasticity_data.round(3), use_container_width=True)
    
    with tab5:
        st.subheader("📡 Monitoring en Temps Reel")
        
        monitoring_data = advanced.create_real_time_monitoring()
        
        # Tableau de monitoring
        st.dataframe(monitoring_data.round(2), use_container_width=True)
        
        # Graphique des changements de prix
        fig = px.bar(
            monitoring_data,
            x='product',
            y='price_change',
            color='status',
            title='Changements de Prix en Temps Reel',
            text='trend'
        )
        fig.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)
        
        # Alertes automatiques
        high_changes = monitoring_data[abs(monitoring_data['price_change']) > 5]
        if not high_changes.empty:
            st.error("🚨 Alertes de Changement Significatif:")
            for _, alert in high_changes.iterrows():
                st.error(f"{alert['product']}: {alert['price_change']:.2f}% {alert['status']}")
    
    with tab6:
        st.subheader("💼 Optimiseur de Portefeuille")
        
        portfolio_data = advanced.create_portfolio_optimizer()
        
        # Metriques du portefeuille
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            avg_return = portfolio_data['expected_return'].mean()
            st.metric("📈 Rendement Moyen", f"{avg_return:.2%}")
        
        with col2:
            avg_volatility = portfolio_data['volatility'].mean()
            st.metric("📊 Volatilite Moyenne", f"{avg_volatility:.2%}")
        
        with col3:
            avg_sharpe = portfolio_data['sharpe_ratio'].mean()
            st.metric("🎯 Sharpe Moyen", f"{avg_sharpe:.3f}")
        
        with col4:
            high_sharpe = len(portfolio_data[portfolio_data['sharpe_ratio'] > 1.0])
            st.metric("🔥 Produits Premium", high_sharpe)
        
        # Graphique risque-rendement
        fig = px.scatter(
            portfolio_data,
            x='volatility',
            y='expected_return',
            size='sharpe_ratio',
            color='risk_category',
            hover_name='product',
            title='Optimisation de Portefeuille - Risque vs Rendement',
            color_discrete_map={
                '🟢 Faible risque': 'green',
                '🟵 Modere': 'blue',
                '🟡 Risque': 'orange',
                '🔴 Tres risque': 'red'
            }
        )
        
        # Ajout de la ligne efficiente (simplifiee)
        fig.add_shape(
            type="line",
            x0=0, y0=0,
            x1=portfolio_data['volatility'].max(),
            y1=portfolio_data['expected_return'].max(),
            line=dict(color="red", dash="dash"),
            name="Frontiere Efficient"
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Recommandations de portefeuille
        st.subheader("💡 Recommandations de Portefeuille")
        
        # Top produits par Sharpe ratio
        top_products = portfolio_data.nlargest(5, 'sharpe_ratio')
        
        st.write("🏆 **Top 5 des Produits Recommandes:**")
        for _, product in top_products.iterrows():
            st.markdown(f"""
            **{product['product']}**
            - Rendement attendu: {product['expected_return']:.2%}
            - Volatilite: {product['volatility']:.2%}
            - Sharpe Ratio: {product['sharpe_ratio']:.3f}
            - Poids recommande: {product['weight_recommendation']}
            - Risque: {product['risk_category']}
            """)
        
        # Tableau complet
        st.dataframe(portfolio_data.round(3), use_container_width=True)
        
        # Export du rapport
        if st.button("📊 Generer Rapport Complet", type="primary"):
            with st.spinner("Generation du rapport avance..."):
                report = advanced.export_advanced_report()
                
                # Conversion en JSON pour le telechargement
                json_report = json.dumps(report, indent=2, default=str)
                
                st.download_button(
                    label="📥 Telecharger Rapport JSON",
                    data=json_report,
                    file_name=f"advanced_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json"
                )
                
                st.success("✅ Rapport genere avec succes!")
