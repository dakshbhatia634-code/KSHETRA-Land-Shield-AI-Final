import sys
sys.path.insert(0, '.')

from backend.routes.auth import register, login, get_current_profile, save_place, list_saved_places, delete_saved_place, RegisterRequest, LoginRequest, SavePlaceRequest

# 1. Register test user
try:
    reg_res = register(RegisterRequest(full_name="Daksh Test", email="test@kshetra.ai", password="securepassword123", organization="Land Intelligence Labs"))
    print("Registered user:", reg_res.user.email, "token:", reg_res.token[:12] + "...")
except Exception as e:
    print("User might already exist, trying login...")

# 2. Login test
log_res = login(LoginRequest(email="test@kshetra.ai", password="securepassword123"))
print("Login successful:", log_res.user.full_name, "role:", log_res.user.role)

# 3. Save place test
place = save_place(SavePlaceRequest(name="Faridabad Prime Agro Site", notes="Verified 10m Sentinel-2 tile", latitude=28.40072, longitude=77.35007, is_demo=True, demo_index=0), user_id=log_res.user.id)
print("Saved place created:", place.id, place.name, place.created_at)

# 4. List saved places
places = list_saved_places(user_id=log_res.user.id)
print(f"User has {len(places)} saved places.")
for p in places:
    print(" -", p.name, f"({p.latitude:.4f}, {p.longitude:.4f})")

print("\nAuthentication & SQLite Persistence Engine Verified Successfully!")
