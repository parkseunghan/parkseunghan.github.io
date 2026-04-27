(function () {
  "use strict";

  var copyTargetIndex = 0;

  var getPageContent = function () {
    return document.querySelector(".page__content");
  };

  var findDirectChild = function (parent, matcher) {
    if (!parent) {
      return null;
    }

    for (var index = 0; index < parent.children.length; index += 1) {
      if (matcher(parent.children[index])) {
        return parent.children[index];
      }
    }

    return null;
  };

  var getWrapperButton = function (wrapper) {
    return findDirectChild(wrapper, function (child) {
      return child.classList && child.classList.contains("clipboard-copy-button");
    });
  };

  var getPreButton = function (pre) {
    return findDirectChild(pre, function (child) {
      return child.classList && child.classList.contains("clipboard-copy-button");
    });
  };

  var getCodeBlock = function (pre) {
    return findDirectChild(pre, function (child) {
      return child.tagName && child.tagName.toLowerCase() === "code";
    });
  };

  var copyText = function (text) {
    if (document.queryCommandEnabled("copy") && navigator.clipboard) {
      navigator.clipboard.writeText(text).then(
        function () {
          return true;
        },
        function () {
          console.error("Failed to copy text to clipboard.");
        }
      );
      return true;
    }

    var isRTL = document.documentElement.getAttribute("dir") === "rtl";
    var textarea = document.createElement("textarea");
    var yPosition = window.pageYOffset || document.documentElement.scrollTop;

    textarea.className = "clipboard-helper";
    textarea.style[isRTL ? "right" : "left"] = "-9999px";
    textarea.style.top = yPosition + "px";
    textarea.setAttribute("readonly", "");
    textarea.value = text;
    document.body.appendChild(textarea);

    var success = true;

    try {
      textarea.select();
      success = document.execCommand("copy");
    } catch (error) {
      success = false;
    }

    document.body.removeChild(textarea);
    return success;
  };

  var toggleCopiedState = function (button) {
    if (button.interval !== null && button.interval !== undefined) {
      clearTimeout(button.interval);
    }

    button.classList.add("copied");
    button.interval = setTimeout(function () {
      button.classList.remove("copied");
      button.interval = null;
    }, 1500);
  };

  var handleCopyClick = function (event) {
    event.preventDefault();
    event.stopPropagation();

    var button = event.currentTarget;
    var targetId = button.getAttribute("data-copy-target");
    var codeBlock = targetId ? document.getElementById(targetId) : null;

    if (!codeBlock) {
      return false;
    }

    var copied = copyText(codeBlock.innerText);
    button.focus();

    if (copied) {
      toggleCopiedState(button);
    }

    return copied;
  };

  var ensureBoundButton = function (button, codeBlock) {
    if (!codeBlock.id) {
      copyTargetIndex += 1;
      codeBlock.id = "code-copy-target-" + copyTargetIndex;
    }

    button.type = "button";
    button.interval = null;
    button.classList.remove("copied");
    button.setAttribute("data-copy-target", codeBlock.id);
    button.setAttribute("aria-label", "Copy code");
    button.title = "Copy to clipboard";

    if (button.dataset.codexCopyBound === "true") {
      return button;
    }

    var replacement = button.cloneNode(true);
    replacement.type = "button";
    replacement.interval = null;
    replacement.classList.remove("copied");
    replacement.setAttribute("data-copy-target", codeBlock.id);
    replacement.setAttribute("aria-label", "Copy code");
    replacement.title = "Copy to clipboard";
    replacement.dataset.codexCopyBound = "true";
    replacement.addEventListener("click", handleCopyClick);
    button.replaceWith(replacement);

    return replacement;
  };

  var relocateCopyButtons = function () {
    var pageContent = getPageContent();

    if (!pageContent) {
      return;
    }

    pageContent.querySelectorAll("pre.highlight").forEach(function (pre) {
      var wrapper = pre.closest("div.highlighter-rouge, figure.highlight");
      var codeBlock = getCodeBlock(pre);

      if (!wrapper || !codeBlock) {
        return;
      }

      var preButton = getPreButton(pre);
      var wrapperButton = getWrapperButton(wrapper);

      if (preButton) {
        if (wrapperButton && wrapperButton !== preButton) {
          wrapperButton.remove();
        }

        wrapper.appendChild(preButton);
        wrapperButton = preButton;
      }

      if (!wrapperButton) {
        return;
      }

      ensureBoundButton(wrapperButton, codeBlock);
    });
  };

  var observeCopyButtons = function () {
    var pageContent = getPageContent();

    if (!pageContent || pageContent.dataset.codexCopyObserver === "true") {
      return;
    }

    var observer = new MutationObserver(function (mutations) {
      var hasChanges = mutations.some(function (mutation) {
        return mutation.addedNodes.length > 0 || mutation.removedNodes.length > 0;
      });

      if (hasChanges) {
        window.requestAnimationFrame(relocateCopyButtons);
      }
    });

    observer.observe(pageContent, {
      childList: true,
      subtree: true,
    });

    pageContent.dataset.codexCopyObserver = "true";
  };

  var initialize = function () {
    relocateCopyButtons();
    observeCopyButtons();
    window.setTimeout(relocateCopyButtons, 0);
    window.setTimeout(relocateCopyButtons, 150);
    window.addEventListener("load", relocateCopyButtons, { once: true });
  };

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initialize);
  } else {
    initialize();
  }
})();
