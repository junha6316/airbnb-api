from rest_framework import serializers

from .models import Room
from users.serializers import RelatedUserSerializer


class RoomSerializer(serializers.ModelSerializer):

    user = RelatedUserSerializer()
    is_fav = serializers.SerializerMethodField() #Dynamic Field

    class Meta:
        model = Room
        exclude = ["modified"]
        read_only_fields = ["user", "id", "created", "updated"]

    def validate(self, data):
        if self.instance:
            #create 할 때만 validation 진행
            check_in = data.get("check_in", self.instance.check_in)
            check_out = data.get("check_out", self.instance.check_out)    
            
        else:
            check_in = data.get("check_in")
            check_out = data.get("check_out")
        
        if check_in == check_out:
                raise serializers.ValidationError("Not enough time between changes")
        return data

    def get_is_fav(self, obj):
        request = self.context.get('request')
        if request:
            user = request.user
            if user.is_authenticated:
                return obj in user.favs.all()
        return False

        

    """
    def validate_fieldname을 이용해 validate 로직 생성 가능
    raise ValidationError('message')
    """    


    

    

    