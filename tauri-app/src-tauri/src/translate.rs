/// Translate text using Google Translate's free API.
/// Auto-detects source language.
pub async fn google_translate(
    text: &str,
    target: &str,
) -> Result<String, Box<dyn std::error::Error + Send + Sync>> {
    let url = format!(
        "https://translate.googleapis.com/translate_a/single?client=gtx&sl=auto&tl={}&dt=t&q={}",
        target,
        urlencoding::encode(text)
    );

    let response = reqwest::get(&url).await?;
    let body = response.text().await?;

    // Parse the response - it's a nested JSON array
    // Format: [[["translated","original","",""],...],null,"detected_lang"]
    let parsed: serde_json::Value = serde_json::from_str(&body)?;

    let mut translated = String::new();
    if let Some(sentences) = parsed.get(0).and_then(|v| v.as_array()) {
        for sentence in sentences {
            if let Some(trans) = sentence.get(0).and_then(|v| v.as_str()) {
                translated.push_str(trans);
            }
        }
    }

    if translated.is_empty() {
        return Err("No translation returned".into());
    }

    Ok(translated)
}
