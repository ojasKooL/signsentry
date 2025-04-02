// Common JavaScript functionality

// Smooth scrolling for anchor links
document.querySelectorAll('a[href^="#"]').forEach((anchor) => {
  anchor.addEventListener("click", function (e) {
    e.preventDefault()

    const targetId = this.getAttribute("href")
    if (targetId === "#") return

    const targetElement = document.querySelector(targetId)
    if (targetElement) {
      window.scrollTo({
        top: targetElement.offsetTop - 80,
        behavior: "smooth",
      })
    }
  })
})

// Add active class to navigation links based on current page
document.addEventListener("DOMContentLoaded", () => {
  const currentLocation = window.location.pathname
  const navLinks = document.querySelectorAll("nav ul li a")

  navLinks.forEach((link) => {
    const linkPath = link.getAttribute("href")
    if (currentLocation.includes(linkPath) && !linkPath.includes("#")) {
      link.classList.add("active")
    } else if (currentLocation.endsWith("/") && linkPath.includes("home")) {
      link.classList.add("active")
    }
  })
})

// Add animation on scroll
document.addEventListener("DOMContentLoaded", () => {
  const animatedElements = document.querySelectorAll(".feature-card, .step, .option-card")

  function checkScroll() {
    animatedElements.forEach((element) => {
      const elementPosition = element.getBoundingClientRect().top
      const screenPosition = window.innerHeight / 1.3

      if (elementPosition < screenPosition) {
        element.classList.add("animate")
      }
    })
  }

  window.addEventListener("scroll", checkScroll)
  checkScroll() // Check on initial load
})

