from flask_login import login_required, current_user
from flask import render_template, url_for, flash, redirect, request, Blueprint, current_app, jsonify, abort
from werkzeug.utils import secure_filename
from math import radians, cos, sin, asin, sqrt
from sqlalchemy.sql.expression import func
from .models import Post, User
from . import db
from PIL import Image, TiffImagePlugin
import logging
from PIL.ExifTags import TAGS
from wtforms import StringField
from wtforms.validators import DataRequired
import os


main = Blueprint('main', __name__)
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
#logging.basicConfig(level=logging.DEBUG)


def cast(v):
    if isinstance(v, TiffImagePlugin.IFDRational):
        return float(v)
    elif isinstance(v, tuple):
        return tuple(cast(t) for t in v)
    elif isinstance(v, bytes):
        return v.decode(errors="replace")
    elif isinstance(v, dict):
        for kk, vv in v.items():
            v[kk] = cast(vv)
        return v
    else: return v

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# helps calculate mile radius for Home Feed 
def haversine(lat1, lon1, lat2, lon2):
    # Convert degrees to radians
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    # Haversine formula
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    # Radius of Earth in miles
    r = 3956
    return c * r  # Distance in miles


@main.route('/upload_post', methods=['GET', 'POST'])
@login_required  # Ensure the user is logged in
def upload_post():
    caption = request.form['caption']
    city_posted_in = request.form['city_posted_in']
    photo = request.files['photo']
    if photo and allowed_file(photo.filename):
        filename = secure_filename(photo.filename)
        photo.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
        

        # Extract metadata
        metadata = {}
        with Image.open(os.path.join(current_app.config['UPLOAD_FOLDER'], filename)) as img:
            metadata['format'] = img.format
            metadata['size'] = img.size  # (width, height)
            metadata['mode'] = img.mode
            
            # Extract EXIF data if available
        try:
            exif_data = img._getexif()
            if exif_data:
                for k, v in exif_data.items():
                    if k in TAGS:
                        v = cast(v)
                    metadata[TAGS[k]] = v
            # Save post and metadata in the database
            new_post = Post(caption=caption, city_posted_in=city_posted_in, photo=filename, user_id=current_user.id, image_metadata=metadata)
            db.session.add(new_post)
            db.session.commit()
            return redirect(url_for('main.profile'))
        except Exception as e:
            print(f"Error processing EXIF data: {e}")
            return redirect(url_for('main.profile'))
    else:
        flash("File type is not allowed.", "danger")
        return redirect(url_for('main.profile'))

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/explore')
def explore():
    return render_template('explore.html')

@main.route('/explore_posts')
def explore_posts():
    # Pagination parameters
    page = request.args.get('page', 1, type=int)
    per_page = 10  # Adjustable number

    # Fetch random posts
    posts = Post.query.order_by(func.random()).paginate(page=page, per_page=per_page, error_out=False)

    data = []
    # Serialize the posts for the response
    for post in posts.items:
        data.append({
            'id': post.id,
            'photo': url_for('static', filename='uploads/' + post.photo),
            'caption': post.caption,
            'username': post.user.username,  
            'city': post.city_posted_in,  
            'date_posted': post.date_posted.strftime('%B %d, %Y')  # Format date as "Month Day, Year"
        })

    return jsonify(data)

@main.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    user = current_user  # Get the current logged-in user

    user_posts = Post.query.filter_by(user_id=current_user.id).order_by(Post.date_posted.desc()).all() 
    user_posts = user_posts if user_posts else []

    if request.method == 'POST':
        try:
            # Fetch data from the form
            gender = request.form.get('gender')
            age = request.form.get('age')
            city = request.form.get('city')
            latitude = request.form.get('latitude')
            longitude = request.form.get('longitude')

            # Update user details conditionally
            if gender:
                user.gender = gender
            if age:
                user.age = int(age)  # Ensure valid integer
            if city:
                user.city = city
            if latitude and longitude:
                # Validate latitude and longitude are numeric
                try:
                    user.latitude = float(latitude)
                    user.longitude = float(longitude)
                except ValueError:
                    flash("Invalid latitude or longitude values.", "error")
                    return redirect(url_for('main.profile'))

            # Save changes
            db.session.commit()
            flash("Profile updated successfully!", "success")
        except Exception as e:
            db.session.rollback()
            flash("An error occurred while updating your profile.", "error")
            print(str(e))  # Log the error for debugging purposes

    # For GET requests, simply render the profile page
    return render_template('profile.html', user=user, posts=user_posts)


@main.route('/community', methods=['GET'])
@login_required
def community():
    radius = request.args.get('radius', 50, type=int)  # Default radius is 50 miles
    current_user_lat = current_user.latitude
    current_user_lon = current_user.longitude

    # Filter users within the radius
    nearby_users = []
    all_users = User.query.all()

    for user in all_users:
        if user.latitude and user.longitude:
            distance = haversine(current_user_lat, current_user_lon, user.latitude, user.longitude)
            if distance <= radius and user != current_user:
                nearby_users.append(user.id)

    # Fetch posts from nearby users
    posts = Post.query.filter(Post.user_id.in_(nearby_users)).order_by(Post.date_posted.desc()).all()

    return render_template('community.html', posts=posts, radius=radius)





@main.route('/delete_post/<int:post_id>', methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.user_id != current_user.id:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    return jsonify({"message": "Post deleted successfully"}), 200

@main.route('/edit_post/<int:post_id>', methods=['POST'])
@login_required
def edit_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.user_id != current_user.id:
        abort(403)
    data = request.get_json()
    post.caption = data.get('caption', post.caption)
    db.session.commit()
    return jsonify({"message": "Caption updated successfully"}), 200



