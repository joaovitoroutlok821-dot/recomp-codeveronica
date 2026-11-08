package org.libsdl.app;

import android.app.Activity;
import android.os.Bundle;
import android.content.SharedPreferences;
import android.content.pm.ActivityInfo;
import android.graphics.Color;
import android.graphics.Typeface;
import android.graphics.drawable.GradientDrawable;
import android.view.Gravity;
import android.view.View;
import android.widget.*;

public final class GameSettingsActivity extends Activity {
  private SharedPreferences p;
  private LinearLayout content;
  private LinearLayout tabs;
  private int activeRed = Color.rgb(235, 18, 32);
  private int panel = Color.rgb(18, 20, 25);
  private int muted = Color.rgb(160, 168, 180);
  private String current = "Gráficos";

  private int dp(float v) { return (int)(v * getResources().getDisplayMetrics().density + 0.5f); }

  public void onCreate(Bundle b) {
    super.onCreate(b);
    setRequestedOrientation(ActivityInfo.SCREEN_ORIENTATION_LANDSCAPE);
    p = getSharedPreferences("recvx_settings", MODE_PRIVATE);
    buildUi();
    show(current);
  }

  private GradientDrawable shape(int color, int stroke, int radius) {
    GradientDrawable d = new GradientDrawable();
    d.setColor(color); d.setCornerRadius(dp(radius));
    if (stroke != 0) d.setStroke(dp(1), stroke);
    return d;
  }

  private TextView text(String value, int size, int color, boolean bold) {
    TextView t = new TextView(this);
    t.setText(value); t.setTextSize(size); t.setTextColor(color);
    if (bold) t.setTypeface(Typeface.DEFAULT, Typeface.BOLD);
    return t;
  }

  private Button button(String label, boolean selected) {
    Button b = new Button(this);
    b.setText(label); b.setTextSize(12); b.setAllCaps(false);
    b.setTextColor(Color.WHITE);
    b.setBackground(shape(selected ? Color.rgb(115, 0, 8) : Color.rgb(28, 25, 28),
                          selected ? activeRed : Color.rgb(95, 42, 45), 8));
    return b;
  }

  private void buildUi() {
    LinearLayout root = new LinearLayout(this);
    root.setOrientation(LinearLayout.HORIZONTAL);
    root.setPadding(dp(12), dp(10), dp(12), dp(10));
    root.setBackgroundColor(Color.rgb(4, 7, 12));

    LinearLayout side = new LinearLayout(this);
    side.setOrientation(LinearLayout.VERTICAL);
    side.setPadding(dp(8), dp(8), dp(8), dp(8));
    side.setBackground(shape(Color.rgb(12, 14, 19), Color.rgb(105, 22, 30), 12));
    TextView brand = text("RESIDENT EVIL\nCODE: VERONICA X", 17, Color.WHITE, true);
    brand.setGravity(Gravity.CENTER);
    brand.setPadding(dp(4), dp(12), dp(4), dp(18));
    side.addView(brand);
    Button back = button("‹  VOLTAR", false);
    back.setOnClickListener(v -> finish());
    side.addView(back, new LinearLayout.LayoutParams(-1, dp(48)));
    TextView section = text("CONFIGURAÇÕES", 13, activeRed, true);
    section.setPadding(dp(8), dp(20), dp(4), dp(8));
    side.addView(section);
    TextView note = text("Ajuste as opções disponíveis para esta versão Android.", 11, muted, false);
    note.setPadding(dp(8), dp(4), dp(8), dp(8));
    side.addView(note);
    root.addView(side, new LinearLayout.LayoutParams(dp(190), -1));

    LinearLayout main = new LinearLayout(this);
    main.setOrientation(LinearLayout.VERTICAL);
    LinearLayout.LayoutParams mp = new LinearLayout.LayoutParams(0, -1, 1);
    mp.leftMargin = dp(12);
    root.addView(main, mp);

    TextView title = text("Configurações", 24, Color.WHITE, true);
    title.setPadding(dp(8), dp(2), dp(8), dp(8));
    main.addView(title);

    tabs = new LinearLayout(this);
    tabs.setOrientation(LinearLayout.HORIZONTAL);
    String[] names = {"Gráficos", "Desempenho", "Controles", "Áudio"};
    for (String n : names) {
      Button t = button(n, n.equals(current));
      LinearLayout.LayoutParams tp = new LinearLayout.LayoutParams(0, dp(44), 1);
      tp.setMargins(dp(3), dp(2), dp(3), dp(8));
      tabs.addView(t, tp);
      t.setOnClickListener(v -> { current = n; refreshTabs(); show(n); });
    }
    main.addView(tabs);

    content = new LinearLayout(this);
    content.setOrientation(LinearLayout.VERTICAL);
    content.setPadding(dp(10), dp(8), dp(10), dp(8));
    content.setBackground(shape(Color.rgb(12, 14, 18), Color.rgb(125, 28, 35), 12));
    ScrollView scroll = new ScrollView(this);
    scroll.setFillViewport(true);
    scroll.addView(content);
    main.addView(scroll, new LinearLayout.LayoutParams(-1, 0, 1));

    LinearLayout footer = new LinearLayout(this);
    footer.setOrientation(LinearLayout.HORIZONTAL);
    Button reset = button("↶  Restaurar padrões", false);
    reset.setOnClickListener(v -> { p.edit().clear().apply(); current = "Gráficos"; refreshTabs(); show(current); });
    Button apply = button("✓  Aplicar", true);
    apply.setOnClickListener(v -> { Toast.makeText(this, "Configurações salvas.", Toast.LENGTH_SHORT).show(); finish(); });
    LinearLayout.LayoutParams fp = new LinearLayout.LayoutParams(0, dp(46), 1);
    fp.setMargins(dp(4), dp(8), dp(4), 0);
    footer.addView(reset, fp); footer.addView(apply, fp);
    main.addView(footer);
    setContentView(root);
  }

  private void refreshTabs() {
    String[] names = {"Gráficos", "Desempenho", "Controles", "Áudio"};
    for (int i = 0; i < tabs.getChildCount(); i++) {
      Button b = (Button)tabs.getChildAt(i);
      b.setBackground(shape(names[i].equals(current) ? Color.rgb(115,0,8) : Color.rgb(28,25,28),
                            names[i].equals(current) ? activeRed : Color.rgb(95,42,45), 8));
    }
  }

  private LinearLayout card(String heading) {
    LinearLayout box = new LinearLayout(this);
    box.setOrientation(LinearLayout.VERTICAL);
    box.setPadding(dp(10), dp(8), dp(10), dp(8));
    box.setBackground(shape(panel, Color.rgb(95, 28, 34), 10));
    TextView h = text(heading, 16, Color.WHITE, true);
    h.setPadding(dp(2), dp(2), dp(2), dp(8));
    box.addView(h);
    return box;
  }

  private void row(LinearLayout box, String label, View control) {
    LinearLayout line = new LinearLayout(this);
    line.setGravity(Gravity.CENTER_VERTICAL);
    line.setOrientation(LinearLayout.HORIZONTAL);
    TextView l = text(label, 13, Color.WHITE, false);
    line.addView(l, new LinearLayout.LayoutParams(0, -2, 1));
    if (control != null) line.addView(control, new LinearLayout.LayoutParams(dp(190), dp(40)));
    LinearLayout.LayoutParams rp = new LinearLayout.LayoutParams(-1, -2);
    rp.bottomMargin = dp(5);
    box.addView(line, rp);
  }

  private void info(LinearLayout box, String label) {
    TextView t = text(label, 12, muted, false);
    t.setPadding(dp(4), dp(5), dp(4), dp(7));
    box.addView(t);
  }

  private Spinner spinner(String[] values, int selected, String key) {
    Spinner s = new Spinner(this);
    s.setAdapter(new ArrayAdapter<String>(this, android.R.layout.simple_spinner_dropdown_item, values));
    s.setSelection(Math.max(0, Math.min(selected, values.length - 1)));
    s.setOnItemSelectedListener(new android.widget.AdapterView.OnItemSelectedListener() {
      public void onNothingSelected(android.widget.AdapterView<?> a) {}
      public void onItemSelected(android.widget.AdapterView<?> a, View v, int pos, long id) {
        p.edit().putInt(key, pos).apply();
      }
    });
    return s;
  }

  private Switch toggle(String label, String key, boolean def) {
    Switch s = new Switch(this);
    s.setText(label); s.setTextColor(Color.WHITE);
    s.setChecked(p.getBoolean(key, def));
    s.setOnCheckedChangeListener((v, on) -> p.edit().putBoolean(key, on).apply());
    return s;
  }

  private void show(String tab) {
    content.removeAllViews();
    if (tab.equals("Gráficos")) {
      LinearLayout split = new LinearLayout(this);
      split.setOrientation(LinearLayout.HORIZONTAL);
      LinearLayout graphics = card("Gráficos");
      LinearLayout quality = card("Imagem e qualidade");
      row(graphics, "Resolução de saída", spinner(new String[]{"720p (1280 × 720)", "1080p (1920 × 1080)"}, p.getInt("resolution", 1), "resolution"));
      info(graphics, "A resolução é aplicada ao iniciar o jogo novamente.");
      row(graphics, "Filtro de imagem", spinner(new String[]{"Bilinear"}, 0, "filter"));
      info(graphics, "Bilinear é o único filtro habilitado no renderer Android atual.");
      info(quality, "Escala de renderização: indisponível no renderer atual.");
      info(quality, "Qualidade, FSR, CAS, nitidez e anti-aliasing: aguardam integração real no runtime.");
      info(quality, "Partículas e proporção manual: não expostas pelo jogo nesta compilação.");
      LinearLayout.LayoutParams cp = new LinearLayout.LayoutParams(0, -2, 1);
      cp.setMargins(dp(4), dp(4), dp(4), dp(4));
      split.addView(graphics, cp); split.addView(quality, cp);
      content.addView(split);
    } else if (tab.equals("Desempenho")) {
      LinearLayout perf = card("Desempenho");
      row(perf, "Contador de FPS", toggle("Exibir FPS", "show_fps", true));
      info(perf, "O contador mostra a taxa de apresentação medida pelo renderer.");
      info(perf, "Limite de FPS e V-Sync: ainda sem controle confiável exposto pelo runtime.");
      info(perf, "Cache de shaders e redução de efeitos: aguardam suporte real.");
      content.addView(perf);
    } else if (tab.equals("Controles")) {
      LinearLayout controls = card("Controles");
      row(controls, "Controles na tela", spinner(new String[]{"Automático", "Sempre mostrar", "Sempre ocultar"}, p.getInt("touch_mode", 0), "touch_mode"));
      info(controls, "No modo automático, os controles táteis somem após o controle físico enviar entrada confirmada.");
      info(controls, "Ao desconectar o controle físico, os controles na tela voltam a aparecer.");
      info(controls, "Mover botões, tamanho e opacidade: editor de layout ainda será integrado.");
      info(controls, "Controle Bluetooth: detecção e envio de comandos precisam ser confirmados no aparelho.");
      content.addView(controls);
    } else {
      LinearLayout audio = card("Áudio");
      info(audio, "Volume geral, música e efeitos ainda não possuem controles reais expostos pelo runtime.");
      content.addView(audio);
    }
  }
}
