from Backend.src.core.security import hash_password, verify_password

# 1. Test Python hash
py_hash = hash_password("admin123")
print("Python generated hash:", py_hash)
print("Python verifies its own hash:", verify_password("admin123", py_hash))

# 2. Test Java hash
java_hash = "$argon2id$v=19$m=16384,t=2,p=1$HFaG8OgpTWVdpOBx6b91ng$8WOFEtz37NJpXtbQl5AQIP+97RGqFqjdg2OFeCO0wcQ"
print("Python verifies Java hash:", verify_password("admin123", java_hash))
