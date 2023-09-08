from rest_framework import serializers
from authentication.models import User


class UserRegSerializer(serializers.ModelSerializer):
    #To include the password2 field
    password2 = serializers.CharField(style={'input_type':'password'},write_only=True)
    class Meta:
        model = User
        fields = ['email','name','password','password2']

        # password should not be displayed when reading or retrieving the object.
        extra_kwargs={
            'password':{'write_only':True}
        }


#Checking if password1 and password2 are equal
    def validate(self, attrs):
        password = attrs.get('password')
        password2 = attrs.get('password2')
        if(password!=password2):
            raise serializers.ValidationError("Password and Confirm Password Do not match!!")
        return attrs
    
    def create(self, validated_data):
        return User.objects.create_user(**validated_data)
    

class UserLoginSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(max_length = 200)
    class Meta:
        model = User
        fields = ['email','password']