-- INSERT INTO Hotels (name, description, location, price_per_night,image_url)
-- VALUES ('Hotel Nile', 'A beautiful hotel by the Nile river.', 'Cairo, Egypt', 100.00,'https://storage.kempinski.com/cdn-cgi/image/w=1920,f=auto,g=auto,fit=scale-down/ki-cms-prod/images/1/0/2/5/65201-1-eng-GB/e42f4a6cc2c5-73654693_4K.jpg'),
--        ('Beach Resort', 'A relaxing beach resort with amazing views.', 'Sharm El Sheikh, Egypt', 150.00,'https://dynamic-media-cdn.tripadvisor.com/media/photo-o/08/90/79/36/mc-park-beach-resort.jpg?w=900&h=500&s=1'),
--        ('Mountain Lodge', 'A cozy lodge in the mountains.', 'Aswan, Egypt', 80.00,'https://pix10.agoda.net/hotelImages/124/1246280/1246280_16061017110043391702.jpg?ca=6&ce=1&s=414x232&ar=16x9');

INSERT INTO Users (full_name, email, password, phone_number)
VALUES ('John Doe', 'john@example.com', 'hashedpassword123', '1234567890');

INSERT INTO Amenities (name, description)
VALUES ('WiFi', 'High-speed internet'), ('Pool', 'Outdoor swimming pool'), ('Gym', 'Fitness center');

INSERT INTO Hotels (name, location, description, price_per_night, image_url, star_rating, total_rooms, contact_number, email)
VALUES ('Grand Hotel', 'Downtown', 'Luxury hotel with great views', 150.00, 'https://pix10.agoda.net/hotelImages/124/1246280/1246280_16061017110043391702.jpg?ca=6&ce=1&s=414x232&ar=16x9', 5, 100, '1234567890', 'contact@grandhotel.com');




INSERT INTO Hotels (name, location, description, price_per_night, image_url, star_rating, total_rooms, contact_number, email)
VALUES ('Ocean Breeze Resort', 'Beachfront', 'Relaxing resort with ocean views', 200.00, 'https://media.istockphoto.com/id/104731717/photo/luxury-resort.jpg?s=612x612&w=0&k=20&c=cODMSPbYyrn1FHake1xYz9M8r15iOfGz9Aosy9Db7mI=', 4, 80, '9876543210', 'info@oceanbreezeresort.com');




INSERT INTO Hotels (name, location, description, price_per_night, image_url, star_rating, total_rooms, contact_number, email)
VALUES ('Cityscape Inn', 'City Center', 'Modern hotel for business travelers', 120.00, 'https://www.hilton.com/im/en/AUAJMES/19122401/auajm-poolsunset.jpg?impolicy=crop&cw=5000&ch=3333&gravity=NorthWest&xposition=0&yposition=1&rw=1280&rh=854', 3, 50, '5551234567', 'book@cityscapeinn.com');



INSERT INTO Hotels (name, location, description, price_per_night, image_url, star_rating, total_rooms, contact_number, email)
VALUES ('Mountain Retreat', 'Hillside', 'Cozy retreat with mountain views', 180.00, 'https://img.freepik.com/free-photo/beautiful-tropical-beach-sea-with-umbrella-chair-around-swimming-pool_74190-1072.jpg', 4, 60, '4449876543', 'reservations@mountainretreat.com');

