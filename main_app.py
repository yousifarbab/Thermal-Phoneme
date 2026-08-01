# تحليل الزمن الحقيقي (يبدأ من 1)
time_data = np.linspace(1, 10, 500)
signal_data = np.sin(time_data * 2) + 0.5 * np.sin(time_data * 4) + 0.2 * np.random.normal(0, 1, 500)

fig = go.Figure()
fig.add_trace(go.Scatter(
    x=time_data,
    y=signal_data,
    mode='lines',
    name='الإشارة الحية',
    line=dict(color='#00CCFF', width=2)
))
fig.update_layout(
    title="تذبذب الإشارة الحرارية في الزمن",
    xaxis_title="الزمن (ثانية)",
    yaxis_title="الشدة",
    height=400,
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)',
    xaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.05)', dtick=1),
    yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.05)')
)
