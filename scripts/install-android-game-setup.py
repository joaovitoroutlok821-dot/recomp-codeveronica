#!/usr/bin/env python3
"""Install a SAF folder-copy launcher into the pinned SDL Android project.

Usage: python3 scripts/install-android-game-setup.py /path/to/SDL/android-project
The selected game tree is copied to app-private storage before SDL starts.
"""
from pathlib import Path
import sys
import xml.etree.ElementTree as ET

if len(sys.argv) != 2:
    raise SystemExit("usage: install-android-game-setup.py /path/to/SDL/android-project")

root = Path(sys.argv[1]).resolve()
app = root / "app"
manifest = app / "src/main/AndroidManifest.xml"
java = app / "src/main/java/org/libsdl/app"
if not manifest.is_file():
    raise SystemExit(f"SDL Android manifest not found: {manifest}")
java.mkdir(parents=True, exist_ok=True)
assets = Path(__file__).resolve().parents[1] / "assets"
# Keep the clean launcher artwork separate from the game cover/logo asset.
# The launcher artwork is shown in-app; the cover/logo image is used for the
# Android app icon so text and settings are never baked into the launcher UI.
cover = assets / "recvx-launcher.png"
logo = assets / "recvx-logo.png"
if not cover.is_file():
    raise SystemExit(f"Approved clean Resident Evil launcher artwork not found: {cover}")
if not logo.is_file():
    raise SystemExit(f"Resident Evil game logo/icon artwork not found: {logo}")
drawable = app / "src/main/res/drawable-nodpi"
mipmap = app / "src/main/res/mipmap-nodpi"
drawable.mkdir(parents=True, exist_ok=True)
mipmap.mkdir(parents=True, exist_ok=True)
(drawable / "recvx_cover.png").write_bytes(cover.read_bytes())
(drawable / "recvx_icon.png").write_bytes(logo.read_bytes())
# SDL ships density-qualified launcher icons. Android prefers those over
# mipmap-nodpi, so replace every existing density variant as well.
res = app / "src/main/res"
icon_dirs = [p for p in res.glob("mipmap-*") if p.is_dir()]
if mipmap not in icon_dirs:
    icon_dirs.append(mipmap)
for icon_dir in icon_dirs:
    (icon_dir / "ic_launcher.png").write_bytes(logo.read_bytes())
    (icon_dir / "ic_launcher_round.png").write_bytes(logo.read_bytes())

# SDL may also ship adaptive-icon XML files, which take precedence over PNG
# density variants on Android 8+. Point those resources at the supplied art.
adaptive_dir = res / "mipmap-anydpi-v26"
if adaptive_dir.is_dir():
    adaptive_xml = """<?xml version="1.0" encoding="utf-8"?>
<adaptive-icon xmlns:android="http://schemas.android.com/apk/res/android">
    <background android:drawable="@android:color/black" />
    <foreground android:drawable="@drawable/recvx_icon" />
</adaptive-icon>
"""
    (adaptive_dir / "ic_launcher.xml").write_text(adaptive_xml, encoding="utf-8")
    (adaptive_dir / "ic_launcher_round.xml").write_text(adaptive_xml, encoding="utf-8")

setup_activity = r'''package org.libsdl.app;

import android.app.Activity;
import android.app.AlertDialog;
import android.content.Intent;
import android.content.pm.ActivityInfo;
import android.content.SharedPreferences;
import android.net.Uri;
import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.os.StatFs;
import android.provider.DocumentsContract;
import android.database.Cursor;
import android.view.Gravity;
import android.view.View;
import android.widget.Button;
import android.widget.ImageView;
import android.widget.FrameLayout;
import android.graphics.Color;
import android.graphics.Typeface;
import android.graphics.drawable.GradientDrawable;
import android.widget.LinearLayout;
import android.widget.ProgressBar;
import android.widget.TextView;
import android.widget.Toast;

import java.io.File;
import java.io.FileOutputStream;
import java.io.FileInputStream;
import java.io.InputStream;
import java.util.ArrayList;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

public final class GameSetupActivity extends Activity {
    private static final int REQUEST_TREE = 4107;
    private static final String PREFS = "game_setup";
    private static final String PREF_URI = "tree_uri";
    private static final String EXTRA_GAME_ROOT = "org.libsdl.app.GAME_ROOT";
    private final ExecutorService worker = Executors.newSingleThreadExecutor();
    private final Handler main = new Handler(Looper.getMainLooper());
    private TextView status;
    private TextView directoryStatus;
    private Button start;
    private Button choose;
    private ProgressBar progress;
    private Uri selectedTree;
    private File gameDir;
    private long totalBytes;
    private long copiedBytes;

    @Override public void onCreate(Bundle state) {
        super.onCreate(state);
        setRequestedOrientation(ActivityInfo.SCREEN_ORIENTATION_LANDSCAPE);
        setTitle("Resident Evil Code Veronica X HD");
        gameDir = new File(getFilesDir(), "game");
        buildUi();
        String saved = getPreferences(MODE_PRIVATE).getString(PREF_URI, null);
        if (saved != null) {
            selectedTree = Uri.parse(saved);
            if (findEntryPoint(gameDir) != null) {
                status.setText("Pasta do jogo preparada. Você pode alterá-la pelo botão SELECIONAR PASTA DO JOGO.");
                start.setEnabled(true);
                refreshDirectoryStatus();
            } else {
                status.setText("Selecione novamente a pasta do jogo para preparar os arquivos.");
            }
        } else {
            status.setText("DIRETÓRIO DO JOGO: Não selecionado. Use SELECIONAR PASTA DO JOGO para escolher a pasta que contém Default.xex.");
        }
    }

    private void buildUi() {
        int pad = (int)(18 * getResources().getDisplayMetrics().density);
        FrameLayout frame = new FrameLayout(this);
        frame.setBackgroundColor(Color.rgb(3, 7, 13));
        int coverId = getResources().getIdentifier("recvx_cover", "drawable", getPackageName());
        if (coverId != 0) {
            ImageView cover = new ImageView(this);
            cover.setImageResource(coverId);
            cover.setScaleType(ImageView.ScaleType.CENTER_CROP);
            frame.addView(cover, new FrameLayout.LayoutParams(-1, -1));
        }
        View shade = new View(this);
        shade.setBackgroundColor(0x77020710);
        frame.addView(shade, new FrameLayout.LayoutParams(-1, -1));

        LinearLayout root = new LinearLayout(this);
        root.setOrientation(LinearLayout.HORIZONTAL);
        root.setPadding(pad, pad, pad, pad);
        LinearLayout menu = new LinearLayout(this);
        menu.setOrientation(LinearLayout.VERTICAL);
        menu.setPadding(pad / 2, pad, pad / 2, pad);
        menu.setGravity(Gravity.CENTER_VERTICAL);
        GradientDrawable menuBg = new GradientDrawable();
        menuBg.setColor(0xDD080B11);
        menuBg.setCornerRadius(dp(18));
        menuBg.setStroke(dp(1), Color.rgb(190, 20, 32));
        menu.setBackground(menuBg);

        TextView brand = new TextView(this);
        brand.setText("RESIDENT EVIL\nCODE: VERONICA X HD");
        brand.setTextColor(Color.WHITE);
        brand.setTextSize(18);
        brand.setTypeface(Typeface.DEFAULT, Typeface.BOLD);
        brand.setGravity(Gravity.CENTER);
        brand.setPadding(pad / 2, pad, pad / 2, pad * 2);
        menu.addView(brand, new LinearLayout.LayoutParams(-1, -2));

        start = new Button(this);
        start.setText("▶  INICIAR JOGO");
        start.setTextSize(15);
        start.setAllCaps(false);
        start.setTextColor(Color.WHITE);
        start.setBackground(roundButton(0xFFE00018));
        start.setOnClickListener(v -> {
            if (findEntryPoint(gameDir) == null) chooseFolder();
            else launchGame();
        });
        LinearLayout.LayoutParams bp = new LinearLayout.LayoutParams(-1, dp(54));
        bp.bottomMargin = pad / 2;
        menu.addView(start, bp);

        Button settings = new Button(this);
        settings.setText("⚙  CONFIGURAÇÕES");
        settings.setTextSize(14);
        settings.setAllCaps(false);
        settings.setTextColor(Color.WHITE);
        settings.setBackground(roundButton(0xCC1A1D24));
        settings.setOnClickListener(v -> startActivity(new Intent(this, GameSettingsActivity.class)));
        menu.addView(settings, new LinearLayout.LayoutParams(-1, dp(50)));

        // Keep SAF folder selection permanently accessible from the launcher.
        // Users must not need to press Start just to choose or change the game directory.
        Button chooseGameFolder = new Button(this);
        chooseGameFolder.setText("▣  SELECIONAR PASTA DO JOGO");
        chooseGameFolder.setTextSize(12);
        chooseGameFolder.setAllCaps(false);
        chooseGameFolder.setTextColor(Color.WHITE);
        chooseGameFolder.setBackground(roundButton(0xCC101820));
        chooseGameFolder.setOnClickListener(v -> chooseFolder());
        LinearLayout.LayoutParams chooseParams = new LinearLayout.LayoutParams(-1, dp(48));
        chooseParams.topMargin = dp(8);
        menu.addView(chooseGameFolder, chooseParams);

        TextView edition = new TextView(this);
        edition.setText("EDIÇÃO DUBLADA • ANDROID");
        edition.setTextColor(Color.rgb(190, 205, 220));
        edition.setTextSize(11);
        edition.setGravity(Gravity.CENTER);
        LinearLayout.LayoutParams ep = new LinearLayout.LayoutParams(-1, -2);
        ep.topMargin = pad;
        menu.addView(edition, ep);
        root.addView(menu, new LinearLayout.LayoutParams(dp(250), -1));

        LinearLayout right = new LinearLayout(this);
        right.setOrientation(LinearLayout.VERTICAL);
        right.setGravity(Gravity.CENTER_VERTICAL);
        right.setPadding(pad, pad, pad, pad);
        LinearLayout.LayoutParams rp = new LinearLayout.LayoutParams(0, -1, 1);
        rp.leftMargin = pad;
        root.addView(right, rp);

        // Use the supplied game artwork directly. Adaptive launcher resources
        // from SDL may otherwise keep displaying the SDL sample logo here.
        int logoId = getResources().getIdentifier("recvx_icon", "drawable", getPackageName());
        if (logoId != 0) {
            ImageView logoView = new ImageView(this);
            logoView.setImageResource(logoId);
            logoView.setScaleType(ImageView.ScaleType.FIT_CENTER);
            right.addView(logoView, new LinearLayout.LayoutParams(dp(210), dp(100)));
        }
        TextView heading = new TextView(this);
        heading.setText("RESIDENT EVIL CODE: VERONICA X HD");
        heading.setTextColor(Color.WHITE);
        heading.setTextSize(24);
        heading.setTypeface(Typeface.DEFAULT, Typeface.BOLD);
        right.addView(heading, new LinearLayout.LayoutParams(-1, -2));

        TextView subtitle = new TextView(this);
        subtitle.setText("EDIÇÃO DUBLADA  •  VERSÃO ANDROID");
        subtitle.setTextColor(Color.rgb(200, 210, 225));
        subtitle.setTextSize(14);
        LinearLayout.LayoutParams sp = new LinearLayout.LayoutParams(-1, -2);
        sp.topMargin = dp(5);
        right.addView(subtitle, sp);

        status = new TextView(this);
        status.setTextColor(Color.WHITE);
        status.setTextSize(15);
        status.setGravity(Gravity.CENTER_VERTICAL);
        status.setPadding(dp(12), dp(10), dp(12), dp(10));
        status.setBackground(roundPanel());
        LinearLayout.LayoutParams stp = new LinearLayout.LayoutParams(-1, -2);
        stp.topMargin = pad;
        right.addView(status, stp);

        progress = new ProgressBar(this, null, android.R.attr.progressBarStyleHorizontal);
        progress.setIndeterminate(true);
        progress.setVisibility(View.GONE);
        LinearLayout.LayoutParams pp = new LinearLayout.LayoutParams(-1, -2);
        pp.topMargin = pad / 2;
        right.addView(progress, pp);

        TextView footer = new TextView(this);
        footer.setText("Selecione a pasta do jogo uma única vez. Os arquivos serão preparados no armazenamento privado do aplicativo.");
        footer.setTextColor(Color.rgb(190, 198, 210));
        footer.setTextSize(12);
        LinearLayout.LayoutParams ftp = new LinearLayout.LayoutParams(-1, -2);
        ftp.topMargin = pad;
        right.addView(footer, ftp);

        // Persistent bottom status bar: the directory item is also the folder picker.
        LinearLayout bottomBar = new LinearLayout(this);
        bottomBar.setOrientation(LinearLayout.HORIZONTAL);
        bottomBar.setGravity(Gravity.CENTER_VERTICAL);
        bottomBar.setPadding(dp(10), dp(5), dp(10), dp(5));
        bottomBar.setBackground(roundPanel());
        directoryStatus = new TextView(this);
        directoryStatus.setTextColor(Color.rgb(255, 220, 45));
        directoryStatus.setTextSize(12);
        directoryStatus.setText("▱  Diretório do jogo: Não selecionado");
        directoryStatus.setOnClickListener(v -> chooseFolder());
        bottomBar.addView(directoryStatus, new LinearLayout.LayoutParams(0, dp(34), 1));
        TextView controllerStatus = new TextView(this);
        controllerStatus.setTextColor(Color.rgb(210, 215, 225));
        controllerStatus.setTextSize(12);
        controllerStatus.setText("♧  Controle: verificar ao iniciar");
        bottomBar.addView(controllerStatus, new LinearLayout.LayoutParams(-2, dp(34)));
        TextView touchStatus = new TextView(this);
        touchStatus.setTextColor(Color.rgb(100, 230, 120));
        touchStatus.setTextSize(12);
        touchStatus.setPadding(dp(12), 0, dp(4), 0);
        touchStatus.setText("  Controles na tela: Ativado");
        bottomBar.addView(touchStatus, new LinearLayout.LayoutParams(-2, dp(34)));
        LinearLayout.LayoutParams bottomParams = new LinearLayout.LayoutParams(-1, -2);
        bottomParams.topMargin = dp(6);
        root.setOrientation(LinearLayout.VERTICAL);
        LinearLayout screenBody = new LinearLayout(this);
        screenBody.setOrientation(LinearLayout.HORIZONTAL);
        screenBody.addView(menu, new LinearLayout.LayoutParams(dp(250), -1));
        screenBody.addView(right, rp);
        root.removeAllViews();
        root.addView(screenBody, new LinearLayout.LayoutParams(-1, 0, 1));
        root.addView(bottomBar, bottomParams);

        frame.addView(root, new FrameLayout.LayoutParams(-1, -1));
        setContentView(frame);
        refreshDirectoryStatus();
    }

    private void refreshDirectoryStatus() {
        if (directoryStatus == null) return;
        boolean ready = findEntryPoint(gameDir) != null;
        directoryStatus.setText(ready
            ? "▱  Diretório do jogo: Selecionado  •  Toque para alterar"
            : "▱  Diretório do jogo: Não selecionado  •  Toque para escolher");
    }

    private int dp(float value) {
        return (int)(value * getResources().getDisplayMetrics().density + 0.5f);
    }

    private GradientDrawable roundButton(int color) {
        GradientDrawable d = new GradientDrawable();
        d.setColor(color);
        d.setCornerRadius(dp(9));
        d.setStroke(dp(1), Color.rgb(180, 24, 36));
        return d;
    }

    private GradientDrawable roundPanel() {
        GradientDrawable d = new GradientDrawable();
        d.setColor(0xCC080B11);
        d.setCornerRadius(dp(9));
        d.setStroke(dp(1), Color.rgb(145, 30, 40));
        return d;
    }

    private void chooseFolder() {
        Intent intent = new Intent(Intent.ACTION_OPEN_DOCUMENT_TREE);
        intent.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION |
                        Intent.FLAG_GRANT_PERSISTABLE_URI_PERMISSION);
        startActivityForResult(intent, REQUEST_TREE);
    }

    @Override protected void onActivityResult(int request, int result, Intent data) {
        super.onActivityResult(request, result, data);
        if (request != REQUEST_TREE || result != RESULT_OK || data == null || data.getData() == null) return;
        Uri tree = data.getData();
        selectedTree = tree;
        try {
            getContentResolver().takePersistableUriPermission(
                tree, data.getFlags() & (Intent.FLAG_GRANT_READ_URI_PERMISSION | Intent.FLAG_GRANT_WRITE_URI_PERMISSION));
        } catch (SecurityException ignored) {
            // The immediate copy can still proceed when a provider does not support persisted grants.
        }
        prepareGame(tree);
    }

    private void prepareGame(Uri tree) {
        start.setEnabled(false);
        start.setEnabled(false);
        progress.setVisibility(View.VISIBLE);
        status.setText("Verificando arquivos e espaço disponível...");
        worker.execute(() -> {
            try {
                validateSourceXex(tree);
                File staging = new File(getFilesDir(), "game.new");
                deleteRecursively(staging);
                if (!staging.mkdirs() && !staging.isDirectory()) throw new Exception("Não foi possível criar a pasta temporária.");
                Uri rootUri = DocumentsContract.buildDocumentUriUsingTree(tree, DocumentsContract.getTreeDocumentId(tree));
                totalBytes = estimateDirectoryBytes(rootUri);
                copiedBytes = 0;
                long available = new StatFs(getFilesDir().getAbsolutePath()).getAvailableBytes();
                long safetyMargin = 128L * 1024L * 1024L;
                if (totalBytes > 0 && totalBytes + safetyMargin > available) {
                    throw new Exception("Espaço insuficiente. Necessário aproximadamente " +
                        formatBytes(totalBytes + safetyMargin) + "; disponível " + formatBytes(available) + ".");
                }
                main.post(() -> {
                    progress.setIndeterminate(totalBytes <= 0);
                    progress.setMax(1000);
                    progress.setProgress(0);
                    status.setText(totalBytes > 0
                        ? "Copiando arquivos: 0% (" + formatBytes(totalBytes) + ")"
                        : "Copiando arquivos. O provedor não informou o tamanho total.");
                });
                copyDirectory(rootUri, staging);
                File entry = findEntryPoint(staging);
                if (entry == null) throw new Exception("Nenhum arquivo .xex válido foi encontrado na raiz da pasta selecionada.");
                File backup = new File(getFilesDir(), "game.old");
                deleteRecursively(backup);
                if (gameDir.exists() && !gameDir.renameTo(backup)) throw new Exception("Não foi possível preservar a cópia anterior.");
                if (!staging.renameTo(gameDir)) {
                    if (backup.exists()) backup.renameTo(gameDir);
                    throw new Exception("Não foi possível finalizar a cópia dos arquivos.");
                }
                deleteRecursively(backup);
                main.post(() -> {
                    progress.setVisibility(View.GONE);
                    start.setEnabled(true);
                    start.setEnabled(true);
                    getPreferences(MODE_PRIVATE).edit().putString(PREF_URI, tree.toString()).apply();
                    status.setText("Arquivos preparados. Toque em INICIAR JOGO para continuar.");
                    Toast.makeText(this, "Pasta do jogo preparada.", Toast.LENGTH_LONG).show();
                });
            } catch (Exception e) {
                deleteRecursively(new File(getFilesDir(), "game.new"));
                main.post(() -> {
                    progress.setVisibility(View.GONE);
                    start.setEnabled(true);
                    start.setEnabled(false);
                    status.setText("Falha ao preparar os arquivos: " + e.getMessage());
                    refreshDirectoryStatus();
                });
            }
        });
    }

    private long estimateDirectoryBytes(Uri directoryUri) throws Exception {
        String documentId = DocumentsContract.getDocumentId(directoryUri);
        Uri children = DocumentsContract.buildChildDocumentsUriUsingTree(directoryUri, documentId);
        String[] columns = {DocumentsContract.Document.COLUMN_DOCUMENT_ID,
                            DocumentsContract.Document.COLUMN_MIME_TYPE,
                            DocumentsContract.Document.COLUMN_SIZE};
        long total = 0;
        try (Cursor cursor = getContentResolver().query(children, columns, null, null, null)) {
            if (cursor == null) throw new Exception("Não foi possível estimar o tamanho da pasta selecionada.");
            int sizeColumn = cursor.getColumnIndex(DocumentsContract.Document.COLUMN_SIZE);
            while (cursor.moveToNext()) {
                String id = cursor.getString(0);
                String mime = cursor.getString(1);
                if (DocumentsContract.Document.MIME_TYPE_DIR.equals(mime)) {
                    long nested = estimateDirectoryBytes(
                        DocumentsContract.buildDocumentUriUsingTree(directoryUri, id));
                    if (nested < 0) return -1;
                    total += nested;
                } else {
                    if (sizeColumn < 0 || cursor.isNull(sizeColumn)) return -1;
                    long size = cursor.getLong(sizeColumn);
                    if (size < 0) return -1;
                    total += size;
                }
            }
        }
        return total;
    }

    private String formatBytes(long bytes) {
        if (bytes >= 1024L * 1024L * 1024L) return String.format(java.util.Locale.ROOT, "%.2f GB", bytes / (1024.0 * 1024.0 * 1024.0));
        if (bytes >= 1024L * 1024L) return String.format(java.util.Locale.ROOT, "%.0f MB", bytes / (1024.0 * 1024.0));
        return String.format(java.util.Locale.ROOT, "%.0f KB", bytes / 1024.0);
    }

    private void copyDirectory(Uri directoryUri, File destination) throws Exception {
        String documentId = DocumentsContract.getDocumentId(directoryUri);
        Uri children = DocumentsContract.buildChildDocumentsUriUsingTree(directoryUri, documentId);
        String[] columns = {DocumentsContract.Document.COLUMN_DOCUMENT_ID,
                            DocumentsContract.Document.COLUMN_DISPLAY_NAME,
                            DocumentsContract.Document.COLUMN_MIME_TYPE,
                            DocumentsContract.Document.COLUMN_SIZE};
        try (Cursor cursor = getContentResolver().query(children, columns, null, null, null)) {
            if (cursor == null) throw new Exception("O provedor de arquivos não retornou a lista da pasta.");
            while (cursor.moveToNext()) {
                String id = cursor.getString(0);
                String name = safeName(cursor.getString(1));
                String mime = cursor.getString(2);
                if (name.isEmpty() || ".".equals(name) || "..".equals(name)) continue;
                Uri child = DocumentsContract.buildDocumentUriUsingTree(directoryUri, id);
                File target = new File(destination, name);
                if (DocumentsContract.Document.MIME_TYPE_DIR.equals(mime)) {
                    if (!target.mkdirs() && !target.isDirectory()) throw new Exception("Não foi possível criar: " + name);
                    copyDirectory(child, target);
                } else {
                    copyFile(child, target);
                }
            }
        }
    }

    private String safeName(String value) {
        if (value == null) return "";
        String name = value.replace('/', '_').replace('\\', '_').trim();
        return name.length() > 240 ? name.substring(0, 240) : name;
    }

    private void copyFile(Uri source, File target) throws Exception {
        File parent = target.getParentFile();
        if (parent != null && !parent.isDirectory() && !parent.mkdirs()) throw new Exception("Falha ao criar diretório.");
        try (InputStream in = getContentResolver().openInputStream(source);
             FileOutputStream out = new FileOutputStream(target)) {
            if (in == null) throw new Exception("Não foi possível abrir um arquivo selecionado.");
            byte[] buffer = new byte[1024 * 1024];
            int count;
            while ((count = in.read(buffer)) != -1) {
                long available = new StatFs(getFilesDir().getAbsolutePath()).getAvailableBytes();
                long safetyMargin = 32L * 1024L * 1024L;
                if (available < count + safetyMargin) {
                    throw new java.io.IOException("Espaço livre insuficiente durante a cópia. Libere armazenamento e tente novamente.");
                }
                out.write(buffer, 0, count);
                copiedBytes += count;
                if (totalBytes > 0) {
                    final int percent = (int)Math.min(1000L, copiedBytes * 1000L / totalBytes);
                    final long copied = copiedBytes;
                    main.post(() -> {
                        progress.setIndeterminate(false);
                        progress.setProgress(percent);
                        status.setText("Copiando arquivos: " + (percent / 10) + "% (" +
                            formatBytes(copied) + " de " + formatBytes(totalBytes) + ")");
                    });
                }
            }
            out.getFD().sync();
        }
    }

    private void launchGame() {
        File entry = findEntryPoint(gameDir);
        if (entry == null) {
            start.setEnabled(false);
            status.setText("Os arquivos do jogo não estão preparados. Selecione a pasta novamente.");
            return;
        }
        Intent intent = new Intent(this, GameSDLActivity.class);
        intent.putExtra(EXTRA_GAME_ROOT, gameDir.getAbsolutePath());
        startActivity(intent);
    }

    private void validateSourceXex(Uri tree) throws Exception {
        Uri children = DocumentsContract.buildChildDocumentsUriUsingTree(
            tree, DocumentsContract.getTreeDocumentId(tree));
        String[] columns = {
            DocumentsContract.Document.COLUMN_DOCUMENT_ID,
            DocumentsContract.Document.COLUMN_DISPLAY_NAME,
            DocumentsContract.Document.COLUMN_MIME_TYPE,
            DocumentsContract.Document.COLUMN_SIZE
        };
        try (Cursor cursor = getContentResolver().query(children, columns, null, null, null)) {
            if (cursor == null) throw new Exception("Não foi possível verificar o arquivo Default.xex.");
            int sizeColumn = cursor.getColumnIndex(DocumentsContract.Document.COLUMN_SIZE);
            while (cursor.moveToNext()) {
                String name = cursor.getString(1);
                String mime = cursor.getString(2);
                if (!"default.xex".equalsIgnoreCase(name) ||
                    DocumentsContract.Document.MIME_TYPE_DIR.equals(mime)) continue;
                if (sizeColumn >= 0 && !cursor.isNull(sizeColumn) &&
                    cursor.getLong(sizeColumn) < 1048576L) {
                    throw new Exception("Default.xex é pequeno demais para ser o executável esperado.");
                }
                Uri document = DocumentsContract.buildDocumentUriUsingTree(tree, cursor.getString(0));
                try (InputStream in = getContentResolver().openInputStream(document)) {
                    if (in == null || in.read() != 'X' || in.read() != 'E' ||
                        in.read() != 'X' || in.read() != '2') {
                        throw new Exception("Default.xex não possui cabeçalho XEX2 válido.");
                    }
                }
                return;
            }
        }
        throw new Exception("Default.xex não foi encontrado na raiz da pasta selecionada.");
    }

    private static boolean isValidXex2(File file) {
        if (!file.isFile() || file.length() < 1048576L) return false;
        try (FileInputStream in = new FileInputStream(file)) {
            return in.read() == 'X' && in.read() == 'E' &&
                   in.read() == 'X' && in.read() == '2';
        } catch (Exception ignored) {
            return false;
        }
    }

    private static File findEntryPoint(File directory) {
        File[] files = directory.listFiles();
        if (files == null) return null;
        for (File file : files) {
            if ("default.xex".equalsIgnoreCase(file.getName()) && isValidXex2(file)) return file;
        }
        return null;
    }

    private static void deleteRecursively(File file) {
        if (file.isDirectory()) {
            File[] children = file.listFiles();
            if (children != null) for (File child : children) deleteRecursively(child);
        }
        if (file.exists()) file.delete();
    }

    @Override protected void onDestroy() {
        super.onDestroy();
        worker.shutdown();
    }
}
'''

game_activity = r'''package org.libsdl.app;

import android.hardware.input.InputManager;
import android.content.SharedPreferences;
import android.os.Bundle;
import android.os.Handler;
import android.os.SystemClock;
import android.util.Log;
import android.view.InputDevice;
import android.view.KeyEvent;
import android.view.MotionEvent;
import android.view.View;
import android.view.ViewGroup;

public final class GameSDLActivity extends SDLActivity
        implements InputManager.InputDeviceListener {
    private static final String EXTRA_GAME_ROOT = "org.libsdl.app.GAME_ROOT";
    static native void nativeSetTouchButton(int button, boolean pressed);
    static native void nativeSetTouchAxis(int axis, float value);
    static native float nativeGetPresentedFps();

    private InputManager inputManager;
    private long lastMotionLogMs;
    private TouchControlsView touchView;
    private int touchMode;

    @Override protected String[] getArguments() {
        String root = getIntent().getStringExtra(EXTRA_GAME_ROOT);
        if (root == null || root.isEmpty()) return new String[0];
        SharedPreferences prefs = getSharedPreferences("recvx_settings", MODE_PRIVATE);
        int resolution = prefs.getInt("resolution", 1);
        String width = resolution == 1 ? "1920" : "1280";
        String height = resolution == 1 ? "1080" : "720";
        return new String[] {
            "--game_data_root=" + root,
            "--window_width=" + width,
            "--window_height=" + height,
            "--present_effect=bilinear"
        };
    }

    @Override protected void onCreate(Bundle state) {
        super.onCreate(state);
        if (!mBrokenLibraries) {
            SharedPreferences prefs = getSharedPreferences("recvx_settings", MODE_PRIVATE);
            touchMode = prefs.getInt("touch_mode", 0);
            touchView = new TouchControlsView(this);
            if (touchMode == 2) touchView.setVisibility(View.GONE);
            addContentView(touchView,
                new ViewGroup.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,
                                           ViewGroup.LayoutParams.MATCH_PARENT));
        }
        inputManager = (InputManager)getSystemService(INPUT_SERVICE);
        if (inputManager != null) {
            inputManager.registerInputDeviceListener(this, new Handler());
        }
        logInputDevices("onCreate");
    }

    @Override protected void onResume() {
        super.onResume();
        logInputDevices("onResume");
    }

    @Override protected void onDestroy() {
        if (inputManager != null) {
            inputManager.unregisterInputDeviceListener(this);
        }
        super.onDestroy();
    }

    private boolean isControllerSource(int source) {
        return (source & InputDevice.SOURCE_CLASS_JOYSTICK) == InputDevice.SOURCE_CLASS_JOYSTICK ||
               (source & InputDevice.SOURCE_GAMEPAD) == InputDevice.SOURCE_GAMEPAD ||
               (source & InputDevice.SOURCE_DPAD) == InputDevice.SOURCE_DPAD;
    }

    private void logInputDevices(String reason) {
        int[] ids = InputDevice.getDeviceIds();
        Log.i("RECVX-INPUT", reason + ": Android reports " + ids.length + " input device(s)");
        for (int id : ids) {
            InputDevice device = InputDevice.getDevice(id);
            if (device != null) {
                Log.i("RECVX-INPUT", "device id=" + id + " name=" + device.getName() +
                    " sources=0x" + Integer.toHexString(device.getSources()) +
                    " vendor=0x" + Integer.toHexString(device.getVendorId()) +
                    " product=0x" + Integer.toHexString(device.getProductId()));
            }
        }
    }

    @Override public void onInputDeviceAdded(int id) {
        InputDevice device = InputDevice.getDevice(id);
        Log.i("RECVX-INPUT", "device added id=" + id +
            (device == null ? "" : " name=" + device.getName() +
                " sources=0x" + Integer.toHexString(device.getSources())));
    }

    @Override public void onInputDeviceChanged(int id) {
        InputDevice device = InputDevice.getDevice(id);
        Log.i("RECVX-INPUT", "device changed id=" + id +
            (device == null ? "" : " name=" + device.getName() +
                " sources=0x" + Integer.toHexString(device.getSources())));
    }

    @Override public void onInputDeviceRemoved(int id) {
        Log.i("RECVX-INPUT", "device removed id=" + id);
        if (touchView != null && touchMode == 0 && !hasPhysicalController()) {
            touchView.setVisibility(View.VISIBLE);
        }
    }

    private boolean hasPhysicalController() {
        for (int id : InputDevice.getDeviceIds()) {
            InputDevice d = InputDevice.getDevice(id);
            if (d != null && !d.isVirtual() && isControllerSource(d.getSources())) return true;
        }
        return false;
    }

    private void confirmPhysicalInput() {
        if (touchView != null && touchMode == 0) touchView.setVisibility(View.GONE);
    }

    @Override public boolean dispatchKeyEvent(KeyEvent event) {
        if (isControllerSource(event.getSource())) {
            Log.i("RECVX-INPUT", "key action=" + event.getAction() +
                " keyCode=" + event.getKeyCode() + " device=" + event.getDeviceId() +
                " source=0x" + Integer.toHexString(event.getSource()));
        }
        if (isControllerSource(event.getSource()) && event.getAction() == KeyEvent.ACTION_DOWN) confirmPhysicalInput();
        return super.dispatchKeyEvent(event);
    }

    @Override public boolean dispatchGenericMotionEvent(MotionEvent event) {
        if (isControllerSource(event.getSource()) &&
            event.getActionMasked() == MotionEvent.ACTION_MOVE) {
            long now = SystemClock.uptimeMillis();
            if (now - lastMotionLogMs >= 1000) {
                lastMotionLogMs = now;
                Log.i("RECVX-INPUT", "motion device=" + event.getDeviceId() +
                    " source=0x" + Integer.toHexString(event.getSource()) +
                    " x=" + event.getAxisValue(MotionEvent.AXIS_X) +
                    " y=" + event.getAxisValue(MotionEvent.AXIS_Y) +
                    " rx=" + event.getAxisValue(MotionEvent.AXIS_RX) +
                    " ry=" + event.getAxisValue(MotionEvent.AXIS_RY) +
                    " hatX=" + event.getAxisValue(MotionEvent.AXIS_HAT_X) +
                    " hatY=" + event.getAxisValue(MotionEvent.AXIS_HAT_Y));
            }
        }
        if (isControllerSource(event.getSource()) && event.getActionMasked() == MotionEvent.ACTION_MOVE) confirmPhysicalInput();
        return super.dispatchGenericMotionEvent(event);
    }
}
'''

touch_controls = r'''package org.libsdl.app;

import android.content.Context;
import android.graphics.Canvas;
import android.graphics.Color;
import android.graphics.Paint;
import android.os.Handler;
import android.os.Looper;
import android.util.SparseArray;
import java.util.Locale;
import android.view.MotionEvent;
import android.view.View;

public final class TouchControlsView extends View {
    private static final int STICK = -1;
    private static final int[] BUTTON_CODES = {0, 1, 2, 3, 4, 6, 9, 10};
    private static final String[] BUTTON_LABELS = {"A", "B", "X", "Y", "BACK", "START", "LB", "RB"};
    private static final float[] BUTTON_X = {0.84f, 0.92f, 0.76f, 0.84f, 0.43f, 0.57f, 0.12f, 0.88f};
    private static final float[] BUTTON_Y = {0.78f, 0.70f, 0.70f, 0.62f, 0.90f, 0.90f, 0.18f, 0.18f};

    private final Paint paint = new Paint(Paint.ANTI_ALIAS_FLAG);
    private final boolean showFps;
    private final android.content.SharedPreferences layoutPrefs;
    private final Handler fpsHandler = new Handler(Looper.getMainLooper());
    private float presentedFps;
    private final Runnable fpsRefresh = new Runnable() {
        @Override public void run() {
            presentedFps = GameSDLActivity.nativeGetPresentedFps();
            invalidate();
            fpsHandler.postDelayed(this, 500);
        }
    };
    private final SparseArray<Integer> pointerTargets = new SparseArray<>();
    private final int[] buttonReferences = new int[21];
    private final boolean[] dpadState = new boolean[4];
    private int stickPointer = -1;
    private float stickX;
    private float stickY;

    public TouchControlsView(Context context) {
        super(context);
        showFps = context.getSharedPreferences("recvx_settings", Context.MODE_PRIVATE).getBoolean("show_fps", true);
        layoutPrefs = context.getSharedPreferences("recvx_settings", Context.MODE_PRIVATE);
        setClickable(true);
        setWillNotDraw(false);
        fpsHandler.post(fpsRefresh);
    }

    private float unit() { return Math.min(getWidth(), getHeight()); }
    private float stickCenterX() { return getWidth() * layoutPrefs.getFloat("touch_stick_x", 0.17f); }
    private float stickCenterY() { return getHeight() * layoutPrefs.getFloat("touch_stick_y", 0.76f); }
    private float stickRadius() { return unit() * 0.135f; }

    private float buttonRadius(int index) {
        return unit() * ((index == 4 || index == 5) ? 0.043f :
                         (index == 6 || index == 7) ? 0.052f : 0.058f);
    }
    private float buttonCenterX(int index) {
        return getWidth() * layoutPrefs.getFloat("touch_btn_x_" + index, BUTTON_X[index]);
    }
    private float buttonCenterY(int index) {
        return getHeight() * layoutPrefs.getFloat("touch_btn_y_" + index, BUTTON_Y[index]);
    }

    private void setButtonReference(int button, boolean down) {
        if (button < 0 || button >= buttonReferences.length) return;
        if (down) {
            if (buttonReferences[button]++ == 0) {
                GameSDLActivity.nativeSetTouchButton(button, true);
            }
        } else if (buttonReferences[button] > 0) {
            if (--buttonReferences[button] == 0) {
                GameSDLActivity.nativeSetTouchButton(button, false);
            }
        }
    }

    private void setDpad(int index, int button, boolean down) {
        if (dpadState[index] != down) {
            dpadState[index] = down;
            GameSDLActivity.nativeSetTouchButton(button, down);
        }
    }

    private void updateStick(float x, float y) {
        float dx = (x - stickCenterX()) / stickRadius();
        float dy = (y - stickCenterY()) / stickRadius();
        float length = (float)Math.sqrt(dx * dx + dy * dy);
        if (length > 1.0f) {
            dx /= length;
            dy /= length;
        }
        if (Math.sqrt(dx * dx + dy * dy) < 0.12) {
            dx = 0;
            dy = 0;
        }
        stickX = dx;
        stickY = dy;
        GameSDLActivity.nativeSetTouchAxis(0, dx);
        GameSDLActivity.nativeSetTouchAxis(1, dy);
        setDpad(0, 11, dy < -0.45f);
        setDpad(1, 12, dy > 0.45f);
        setDpad(2, 13, dx < -0.45f);
        setDpad(3, 14, dx > 0.45f);
        invalidate();
    }

    private int hitButton(float x, float y) {
        for (int i = 0; i < BUTTON_CODES.length; ++i) {
            float dx = x - buttonCenterX(i);
            float dy = y - buttonCenterY(i);
            float radius = buttonRadius(i) * 1.55f;
            if (dx * dx + dy * dy <= radius * radius) return i;
        }
        return -1;
    }

    private boolean hitStick(float x, float y) {
        float dx = x - stickCenterX();
        float dy = y - stickCenterY();
        float radius = stickRadius() * 1.5f;
        return dx * dx + dy * dy <= radius * radius;
    }

    private void releasePointer(int id) {
        Integer target = pointerTargets.get(id);
        if (target == null) return;
        pointerTargets.remove(id);
        if (target == STICK) {
            if (stickPointer == id) {
                stickPointer = -1;
                stickX = 0;
                stickY = 0;
                GameSDLActivity.nativeSetTouchAxis(0, 0);
                GameSDLActivity.nativeSetTouchAxis(1, 0);
                setDpad(0, 11, false);
                setDpad(1, 12, false);
                setDpad(2, 13, false);
                setDpad(3, 14, false);
            }
        } else {
            setButtonReference(BUTTON_CODES[target], false);
        }
        invalidate();
    }

    @Override protected void onDraw(Canvas canvas) {
        super.onDraw(canvas);
        float base = unit();
        if (base <= 0) return;

        paint.setStyle(Paint.Style.FILL);
        paint.setColor(Color.argb(38, 255, 255, 255));
        canvas.drawCircle(stickCenterX(), stickCenterY(), stickRadius(), paint);
        paint.setStyle(Paint.Style.STROKE);
        paint.setStrokeWidth(base * 0.006f);
        paint.setColor(Color.argb(150, 255, 255, 255));
        canvas.drawCircle(stickCenterX(), stickCenterY(), stickRadius(), paint);
        paint.setStyle(Paint.Style.FILL);
        paint.setColor(Color.argb(115, 230, 230, 230));
        canvas.drawCircle(stickCenterX() + stickX * stickRadius() * 0.68f,
                          stickCenterY() + stickY * stickRadius() * 0.68f,
                          stickRadius() * 0.36f, paint);

        for (int i = 0; i < BUTTON_CODES.length; ++i) {
            float cx = buttonCenterX(i);
            float cy = buttonCenterY(i);
            float radius = buttonRadius(i);
            paint.setStyle(Paint.Style.FILL);
            paint.setColor(Color.argb(72, 245, 245, 245));
            canvas.drawCircle(cx, cy, radius, paint);
            paint.setStyle(Paint.Style.STROKE);
            paint.setStrokeWidth(base * 0.005f);
            paint.setColor(Color.argb(175, 255, 255, 255));
            canvas.drawCircle(cx, cy, radius, paint);
            paint.setStyle(Paint.Style.FILL);
            paint.setTextAlign(Paint.Align.CENTER);
            paint.setTextSize(radius * ((i == 4 || i == 5 || i == 6 || i == 7) ? 0.48f : 0.9f));
            paint.setColor(Color.WHITE);
            canvas.drawText(BUTTON_LABELS[i], cx, cy + paint.getTextSize() * 0.34f, paint);
        }

        if (showFps) {
        paint.setStyle(Paint.Style.FILL);
        paint.setTextAlign(Paint.Align.LEFT);
        paint.setTextSize(base * 0.035f);
        paint.setColor(Color.argb(220, 255, 255, 255));
        String fpsText = presentedFps > 0.0f
            ? String.format(Locale.US, "FPS %.1f", presentedFps) : "FPS --";
        canvas.drawText(fpsText, getWidth() * 0.035f, getHeight() * 0.075f, paint);
        }
    }

    @Override protected void onDetachedFromWindow() {
        fpsHandler.removeCallbacks(fpsRefresh);
        super.onDetachedFromWindow();
    }

    @Override public boolean onTouchEvent(MotionEvent event) {
        int action = event.getActionMasked();
        if (action == MotionEvent.ACTION_DOWN || action == MotionEvent.ACTION_POINTER_DOWN) {
            int index = event.getActionIndex();
            int id = event.getPointerId(index);
            float x = event.getX(index);
            float y = event.getY(index);
            int button = hitButton(x, y);
            if (button >= 0) {
                pointerTargets.put(id, button);
                setButtonReference(BUTTON_CODES[button], true);
                invalidate();
                return true;
            }
            if (stickPointer < 0 && hitStick(x, y)) {
                stickPointer = id;
                pointerTargets.put(id, STICK);
                updateStick(x, y);
                return true;
            }
            return pointerTargets.size() > 0;
        }

        if (action == MotionEvent.ACTION_MOVE) {
            for (int i = 0; i < event.getPointerCount(); ++i) {
                int id = event.getPointerId(i);
                Integer target = pointerTargets.get(id);
                if (target != null && target == STICK) {
                    updateStick(event.getX(i), event.getY(i));
                }
            }
            return pointerTargets.size() > 0;
        }

        if (action == MotionEvent.ACTION_UP || action == MotionEvent.ACTION_POINTER_UP) {
            releasePointer(event.getPointerId(event.getActionIndex()));
            return true;
        }

        if (action == MotionEvent.ACTION_CANCEL) {
            for (int i = pointerTargets.size() - 1; i >= 0; --i) {
                releasePointer(pointerTargets.keyAt(i));
            }
            return true;
        }
        return pointerTargets.size() > 0;
    }
}
'''

(java / "GameSettingsActivity.java").write_text(
    (Path(__file__).resolve().parent / "android" / "GameSettingsActivity.java").read_text(encoding="utf-8"),
    encoding="utf-8")
(java / "TouchLayoutEditorActivity.java").write_text(
    (Path(__file__).resolve().parent / "android" / "TouchLayoutEditorActivity.java").read_text(encoding="utf-8"),
    encoding="utf-8")
(java / "GameSetupActivity.java").write_text(setup_activity, encoding="utf-8")
(java / "GameSDLActivity.java").write_text(game_activity, encoding="utf-8")
(java / "TouchControlsView.java").write_text(touch_controls, encoding="utf-8")

tree = ET.parse(manifest)
mroot = tree.getroot()
ns = "{http://schemas.android.com/apk/res/android}"
app_node = mroot.find("application")
if app_node is None:
    raise SystemExit("AndroidManifest.xml has no application element")
app_node.set(ns + "label", "Resident Evil Code Veronica X HD")
app_node.set(ns + "icon", "@mipmap/ic_launcher")
app_node.set(ns + "roundIcon", "@mipmap/ic_launcher_round")

# Convert the existing SDLActivity entry into the non-launcher game activity.
sdl = None
for activity in app_node.findall("activity"):
    name = activity.get(ns + "name", "")
    if name.endswith("SDLActivity") and not name.endswith("GameSDLActivity"):
        sdl = activity
        break
if sdl is None:
    raise SystemExit("Could not find the existing SDLActivity manifest entry")
sdl.set(ns + "name", "org.libsdl.app.GameSDLActivity")
sdl.set(ns + "exported", "false")
for filt in list(sdl.findall("intent-filter")):
    actions = [x.get(ns + "name") for x in filt.findall("action")]
    if "android.intent.action.MAIN" in actions:
        sdl.remove(filt)

# Avoid duplicate settings activity if the installer is run more than once.
for activity in list(app_node.findall("activity")):
    if activity.get(ns + "name") == "org.libsdl.app.GameSettingsActivity":
        app_node.remove(activity)
settings_node = ET.Element("activity", {
    ns + "name": "org.libsdl.app.GameSettingsActivity",
    ns + "exported": "false",
    ns + "label": "Configurações"
})
app_node.insert(0, settings_node)

# Register the visual touch-layout editor.
for activity in list(app_node.findall("activity")):
    if activity.get(ns + "name") == "org.libsdl.app.TouchLayoutEditorActivity":
        app_node.remove(activity)
editor_node = ET.Element("activity", {
    ns + "name": "org.libsdl.app.TouchLayoutEditorActivity",
    ns + "exported": "false",
    ns + "label": "Personalizar controles",
    ns + "screenOrientation": "landscape"
})
app_node.insert(0, editor_node)

# Avoid duplicate setup activity if the installer is run more than once.
for activity in list(app_node.findall("activity")):
    if activity.get(ns + "name") == "org.libsdl.app.GameSetupActivity":
        app_node.remove(activity)
setup = ET.Element("activity", {
    ns + "name": "org.libsdl.app.GameSetupActivity",
    ns + "exported": "true",
    ns + "label": "@string/app_name"
})
intent_filter = ET.SubElement(setup, "intent-filter")
ET.SubElement(intent_filter, "action", {ns + "name": "android.intent.action.MAIN"})
ET.SubElement(intent_filter, "category", {ns + "name": "android.intent.category.LAUNCHER"})
app_node.insert(0, setup)

ET.register_namespace("android", "http://schemas.android.com/apk/res/android")
tree.write(manifest, encoding="utf-8", xml_declaration=True)
print("[android-game-setup] SAF setup screen and SDL launch activity installed")
print("[android-game-setup] Selected folder is copied to app-private files/game before runtime launch")
