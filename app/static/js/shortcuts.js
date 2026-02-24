window.addEventListener(
    "keydown",
    e => {
      if (e.ctrlKey && e.altKey && e.code === "KeyS") {
        e.preventDefault();
        window.location.assign("/settings");
      }
    },
    true
  );
  