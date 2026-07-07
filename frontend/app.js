// API base comes from .env (VITE_API_BASE), injected at build time by Vite.
$(function () {
  const API_URL = import.meta.env.VITE_API_BASE + "generate-brief/";
  const $form = $("#brief-form");
  const $btn = $("#submit-btn");
  const $error = $("#error");
  const $result = $("#result");
  const $resultContent = $("#result-content");
  const $resultPlaceholder = $(
    "#result-placeholder"
  );

  // Clear the previous result and fall back to the placeholder.
  function resetResult() {
    $resultContent.attr("hidden", true);
    $("#result-brief").text("");
    $("#result-angles, #result-criteria").empty();
    $("#result-stats").text("");
    $resultPlaceholder.removeAttr("hidden");
  }

  // Pill selection: one active per group.
  $(".pills").on("click", ".pill", function () {
    $(this)
      .addClass("is-active")
      .siblings()
      .removeClass("is-active");
  });

  function selected(name) {
    return $(
      `.pills[data-name="${name}"] .pill.is-active`
    ).data("value");
  }

  function showError(msg) {
    resetResult();
    $error.text(msg).removeAttr("hidden");
  }

  function loading(on) {
    $btn
      .prop("disabled", on)
      .toggleClass("is-loading", on);
    $btn
      .find(".btn__label")
      .text(
        on ? "Generating…" : "Generate Brief"
      );
  }

  $form.on("submit", function (e) {
    e.preventDefault();
    $error.attr("hidden", true);
    resetResult();

    const payload = {
      target: selected("target"),
      goal: selected("goal"),
      tone: selected("tone"),
      brand_name: $("#brand_name").val().trim(),
    };

    // Client-side check mirrors the backend's required fields.
    if (
      !payload.target ||
      !payload.goal ||
      !payload.tone
    ) {
      return showError(
        "Please select a target, goal, and tone."
      );
    }
    if (!payload.brand_name) {
      return showError(
        "Please enter a brand name."
      );
    }

    loading(true);
    $.ajax({
      url: API_URL,
      method: "POST",
      contentType: "application/json",
      data: JSON.stringify(payload),
    })
      .done(render)
      .fail(handleError)
      .always(() => loading(false));
  });

  function render(data) {
    $("#result-brief").text(data.brief || "");

    const fill = ($ul, items) =>
      $ul
        .empty()
        .append(
          (items || []).map((t) =>
            $("<li>").text(t)
          )
        );
    fill($("#result-angles"), data.angles);
    fill($("#result-criteria"), data.criteria);

    const s = data.stats || {};
    $("#result-stats").text(
      `model: ${s.model} · tokens: ${s.total_tokens} · ${s.latency_ms}ms`
    );

    $error.attr("hidden", true);
    $resultPlaceholder.attr("hidden", true);
    $resultContent.removeAttr("hidden");
  }

  function handleError(xhr) {
    if (xhr.status === 0) {
      return showError(
        "Could not reach the server. Check your connection or that the API allows this origin."
      );
    }
    if (xhr.status === 429) {
      return showError(
        "Too many requests. Please wait a minute and try again."
      );
    }

    const body = xhr.responseJSON;
    if (
      xhr.status === 400 &&
      body &&
      typeof body === "object"
    ) {
      // DRF validation errors: { field: ["message", ...] }
      const msgs = Object.entries(body)
        .map(
          ([field, errs]) =>
            `${field}: ${[]
              .concat(errs)
              .join(" ")}`
        )
        .join("\n");
      return showError(
        msgs || "Please check your input."
      );
    }
    if (body && body.error) {
      return showError(body.error);
    }
    showError(
      "Something went wrong. Please try again."
    );
  }
});
